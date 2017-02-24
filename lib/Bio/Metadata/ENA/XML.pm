# Copyright 2015 European Molecular Biology Laboratory - European Bioinformatics Institute
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
package Bio::Metadata::ENA::XML;

use strict;
use warnings;
use Data::Dumper;
use utf8;
use Moose;
use namespace::autoclean;
use Bio::Metadata::Loader::XLSXExperimentLoader;
use Moose::Util::TypeConstraints;

use Bio::Metadata::ENA::SUBValidation;
#use Bio::Metadata::ENA::STDValidation;
#use Bio::Metadata::ENA::EXPRValidation;
#use Bio::Metadata::ENA::RUNValidation;
use Bio::Metadata::Reporter::BasicReporter;

has 'rule_set' => (
  is  => 'rw',
  isa => 'Bio::Metadata::Rules::RuleSet'
);

has 'sub' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_sub   => 'elements',
    add_sub   => 'push',
    count_sub => 'count',
    get_sub   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

# has 'std' => (
#   traits  => ['Array'],
#   is      => 'rw',
#   isa     => 'Bio::Metadata::EntityArrayRef',
#   handles => {
#     all_std   => 'elements',
#     add_std   => 'push',
#     count_std => 'count',
#     get_std   => 'get',
#   },
#   default => sub { [] },
#   coerce  => 1,
# );

# has 'expr' => (
#   traits  => ['Array'],
#   is      => 'rw',
#   isa     => 'Bio::Metadata::EntityArrayRef',
#   handles => {
#     all_expr   => 'elements',
#     add_expr   => 'push',
#     count_expr => 'count',
#     get_expr   => 'get',
#   },
#   default => sub { [] },
#   coerce  => 1,
# );

# has 'run' => (
#   traits  => ['Array'],
#   is      => 'rw',
#   isa     => 'Bio::Metadata::EntityArrayRef',
#   handles => {
#     all_run   => 'elements',
#     add_run   => 'push',
#     count_run => 'count',
#     get_run   => 'get',
#   },
#   default => sub { [] },
#   coerce  => 1,
# );

has 'sub_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::SUBValidation',
  default => sub { Bio::Metadata::ENA::SUBValidation->new },
);

# has 'std_validator' => (
#   is      => 'rw',
#   isa     => 'Bio::Metadata::ENA::STDValidation',
#   default => sub { Bio::Metadata::ENA::STDValidation->new },
# );

# has 'expr_validator' => (
#   is      => 'rw',
#   isa     => 'Bio::Metadata::ENA::EXPRValidation',
#   default => sub { Bio::Metadata::ENA::EXPRValidation->new },
# );

# has 'run_validator' => (
#   is      => 'rw',
#   isa     => 'Bio::Metadata::ENA::RUNValidation',
#   default => sub { Bio::Metadata::ENA::RUNValidation->new },
# );

sub read {
  my ( $self, $file_path ) = @_;

  die("[ERROR] Please provide the path to a XLSX file") if !$file_path;

  my $loader = Bio::Metadata::Loader::XLSXExperimentLoader->new();

  $self->sub( $loader->load_sub_entities($file_path) );
  #$self->std( $loader->load_std_entities($file_path) );
  #$self->exprena( $loader->load_exprena_entities($file_path) );
  #$self->exprfaang( $loader->load_exprfaang_entities($file_path) );
  #$self->run( $loader->load_run_entities($file_path) );
}

sub validate {
  my ($self) = @_;
  my $sub_errors = $self->sub_validator->validate_sub( $self->sub );
  #my $std_errors = $self->std_validator->validate_std( $self->std );
  #my $expr_errors = $self->expr_validator->validate_expr( $self->expr );
  #my $run_errors = $self->run_validator->validate_run( $self->run );
  my $subref_errors =
    $self->sub_validator->check_term_source_refs( $self->sub);
  #my $stdref_errors =
  #  $self->std_validator->check_term_source_refs( $self->std);
  #my $exprref_errors =
  #  $self->expr_validator->check_term_source_refs( $self->expr);
  #my $runref_errors =
  #  $self->run_validator->check_term_source_refs( $self->run);
  #push @$sub_errors, @$std_errors, @$expr_errors, @$run_errors, 
  #@$subref_errors, @$stdref_errors, @$exprref_errors, @$runref_errors;
  push @$sub_errors, @$subref_errors;
  return $sub_errors;
}

sub report_sub {
  my ($self) = @_;

  my $xml_header ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
  my $sub_header ="<SUBMISSION_SET  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.submission.xsd\">\n";
  my $sub_footer ="</SUBMISSION_SET>";

  my $output = $xml_header.$sub_header;

  my ($alias, $center_name, @actions, $holduntil);
  my %schema = (
    "STUDY XML FILENAME" => "study",
    "EXPERIMENT XML FILENAME" => "experiment",
    "RUN XML FILENAME" => "run",
  );
  for my $e ( $self->all_sub ) {
    for my $a ($e->all_attributes) {

      next if ! defined $a->value;

      if ($a->name eq 'alias'){
        $alias = $a->value;
      }
      elsif ($a->name eq 'center_name'){
        $center_name = $a->value;
      }
      elsif($a->name eq "STUDY XML FILENAME" || $a->name eq "EXPERIMENT XML FILENAME" || $a->name eq "RUN XML FILENAME"){
        push(@actions, "\t\t\t<ACTION>\n");
        push(@actions, "\t\t\t\t<ADD source=\"".$a->value."\" schema=\"".$schema{$a->name}."\"/>\n");
        push(@actions, "\t\t\t</ACTION>\n");
      }elsif ($a->name eq 'HoldUntilDate'){
        $holduntil = $a->value;
      }
    }
  }

  $output = $output."\t<SUBMISSION alias=\"".$alias."\" center_name=\"".$center_name."\">\n";
  $output = $output."\t\t<ACTIONS>\n";
  $output = $output.join("", @actions);
  if ($holduntil){
    $output = $output."\t\t\t<ACTION>\n\t\t\t\t<HOLD>\n\t\t\t\t\t<HoldUntilDate=\"".$holduntil."\"/>\n\t\t\t\t</HOLD>\n\t\t\t</ACTION>\n";
  }else{
    $output = $output."\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n";
  }
  $output = $output."\t\t</ACTIONS>\n\t</SUBMISSION>\n".$sub_footer;
}

#sub report_std {
#  my ($self) = @_;

#}

#sub report_expr {
#  my ($self) = @_;

#}

#sub report_run {
#  my ($self) = @_;

#}

1;