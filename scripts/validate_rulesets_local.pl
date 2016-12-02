#!/usr/bin/env perl
use strict;
use warnings;

use BioSD;

use Bio::Metadata::Loader::JSONRuleSetLoader;
use Bio::Metadata::Validate::Support::BioSDLookup;
use Bio::Metadata::Reporter::TextReporter;
use Bio::Metadata::Reporter::ExcelReporter;
use Bio::Metadata::Reporter::BasicReporter;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Bio::Metadata::Loader::XMLExperimentLoader;
use Getopt::Long;
use Data::Dumper;
use Carp;
use List::Util qw(none);

my $rule_file     = undef;
my $rule_type     = undef;
my $data_file     = undef;
my $verbose       = undef;
my $output        = undef;
my $summary       = undef;
my $output_format = undef;

my @valid_output_mdoes = qw(text excel json);
my @valid_rule_types = qw(samples experiments);
my $output_format_string = join( '|', @valid_output_mdoes );
my $type_format_string  = join( '|', @valid_rule_types );

GetOptions(
  "rules=s"         => \$rule_file,
  "ruletype=s"      => \$rule_type,
  "data=s"          => \$data_file,
  "verbose"         => \$verbose,
  "output=s"        => \$output,
  "output_format=s" => \$output_format,
  "summary"         => \$summary,
);

croak "-rules <file> is required"                unless $rule_file;
croak "-rules <file> must exist and be readable" unless -r $rule_file;
croak "-ruletype ($type_format_string) is required" unless $rule_type;
croak "-data <ID> is required"                   unless $data_file;

croak
"no output requested, use -summary and/or -output <file> -output_format $output_format_string"
  unless ( $summary || $output );
croak "please specify -output_format $output_format_string"
  if ( $output && !$output_format );
croak "please specify -output <file>" if ( $output_format && !$output );
croak
"-output_format $output_format is invalid; should be one of $output_format_string"
  if ( $output_format && none { $_ eq $output_format } @valid_output_mdoes );
croak
"-ruletype $rule_type is invalid; should be one of $type_format_string"
  if ( $rule_type && none { $_ eq $rule_type } @valid_rule_types );

my ($loader, $metadata, $entity_status, $entity_outcomes, $attribute_status, $attribute_outcomes, $entity_rule_groups);

my $validator = create_validator( $rule_file, $verbose );

if ($rule_type eq "samples"){

  $loader = Bio::Metadata::Loader::XLSXBioSampleLoader->new();
  $metadata = $loader->load($data_file);
}elsif ($rule_type eq "experiments"){
  $loader = Bio::Metadata::Loader::XMLExperimentLoader->new();
  $metadata = $loader->load($data_file);
}

(
  $entity_status,      $entity_outcomes, $attribute_status,
  $attribute_outcomes, $entity_rule_groups,
) = $validator->check_all($metadata);

print_summary( $entity_status, $attribute_status ) if ($summary);

write_output(
  $output,
  $output_format,
  {
    entities           => $metadata,
    entity_status      => $entity_status,
    entity_outcomes    => $entity_outcomes,
    attribute_status   => $attribute_status,
    attribute_outcomes => $attribute_outcomes,
  }
) if ($output);

sub create_validator {
  my ( $rule_file, $verbose ) = @_;

  my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();
  print "Attempting to load $rule_file$/" if $verbose;
  my $rule_set = $loader->load($rule_file);
  print 'Loaded ' . $rule_set->name . $/ if $verbose;

  my $validator =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  return $validator;
}

sub print_summary {
  my ( $entity_status, $attribute_status ) = @_;

  for ( [ 'samples', $entity_status ], [ 'attributes', $attribute_status ] ) {
    my $title       = $_->[0];
    my $status_hash = $_->[1];

    my $total = scalar( keys %$status_hash );
    my %status_counts;
    map { $status_counts{$_}++ } values %$status_hash;

    print "$total $title - ";
    print join( '; ',
      map { $_ . '(' . $status_counts{$_} . ')' } sort keys %status_counts );
    print $/;
  }
}

sub write_output {
  my ( $output, $output_format, $validator_output ) = @_;

  my $reporter;
  if ( $output_format eq 'text' ) {
    $reporter = Bio::Metadata::Reporter::TextReporter->new();
  }
  elsif ( $output_format eq 'excel'){
    $reporter = Bio::Metadata::Reporter::ExcelReporter->new();
  }
  elsif ($output_format eq 'json'){
    $reporter = Bio::Metadata::Reporter::BasicReporter->new();
  }

  if ( $output eq 'stdout' || $output eq '-' ) {
    $reporter->file_handle( \*STDOUT );
  }
  else {
    $reporter->file_path($output);
  }

  $reporter->report(
    entities           => $metadata,
    entity_status      => $entity_status,
    entity_outcomes    => $entity_outcomes,
    attribute_status   => $attribute_status,
    attribute_outcomes => $attribute_outcomes,
  );
}