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
package Bio::Metadata::BioSample::SampleTab;

use strict;
use warnings;
use Data::Dumper;
use utf8;
use Moose;
use namespace::autoclean;
use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Moose::Util::TypeConstraints;

use Bio::Metadata::BioSample::MSIValidation;
use Bio::Metadata::Reporter::BasicReporter;

has 'scd' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_scd   => 'elements',
    add_scd   => 'push',
    count_scd => 'count',
    get_scd   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'rule_set' => (
  is  => 'rw',
  isa => 'Bio::Metadata::Rules::RuleSet'
);

has 'msi' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_msi   => 'elements',
    add_msi   => 'push',
    count_msi => 'count',
    get_msi   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'msi_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::BioSample::MSIValidation',
  default => sub { Bio::Metadata::BioSample::MSIValidation->new },
);

has 'term_source_ref_use' => (
  is      => 'rw',
  isa     => 'HashRef[Int]',
  traits  => ['Hash'],
  handles => {
    'get_term_source_ref_use' => 'get',
    'set_term_source_ref_use' => 'set',
  }
);

#accepeted Named Attributes. For definition see: https://www.ebi.ac.uk/biosamples/help/st_scd.html
my %named =
  map { $_ => 1 } ( "Organism", "Material", "Sex", "Sample Description" );

#accepted Relationships. For definition see: https://www.ebi.ac.uk/biosamples/help/st_scd.html
my %relationships = map { $_ => 1 } ( "Same as", "Derived from", "Child of" );

sub read {
  my ( $self, $file_path ) = @_;

  die("[ERROR] Please provide the path to a XLSX file") if !$file_path;

  my $loader = Bio::Metadata::Loader::XLSXBioSampleLoader->new();

  $self->msi( $loader->load_msi_entities($file_path) );
  $self->scd( $loader->load_scd_entities($file_path) );
  $self->_tally_term_source_ref_use();
}

sub _increment_term_source_ref_use {
  my ( $self, $term_source_ref ) = @_;
  my $count = $self->get_term_source_ref_use($term_source_ref) // 0;
  $count++;
  $self->set_term_source_ref_use( $term_source_ref, $count );
  return $count;
}

sub _tally_term_source_ref_use {
  my ($self) = @_;

  for my $entity ( $self->all_scd ) {
    for my $attribute ( $entity->all_attributes ) {
      $self->_increment_term_source_ref_use( $attribute->source_ref )
        if ( defined $attribute->source_ref );
    }
  }
}

sub validate {
  my ($self) = @_;
  my $msi_errors = $self->msi_validator->validate_msi( $self->msi );
  my $ref_errors =
    $self->msi_validator->check_term_source_refs( $self->msi, $self->scd );
  push @$msi_errors, @$ref_errors;
  return $msi_errors;
}

sub report_msi {
  my ($self) = @_;

  my $col_sep  = "\t";
  my $line_sep = "\n";
  my $output ="[MSI]$line_sep";
  my @term_sources;
  my @persons;

  my ($seen_submission_version, $seen_submission_ref_layer);

  for my $e ( $self->all_msi ) {
    for my $a ($e->all_attributes) {

      next if ! defined $a->value;

      if ($a->name eq 'Submission Version'){
        $seen_submission_version++;
      }
      if ($a->name eq 'Submission Reference Layer'){
        $seen_submission_ref_layer++;
      }
      if ( $a->name =~ /Person/ ) {
         if ($a->name eq 'Person Last Name'){
           push @persons,{lastname => $a->value, initials => '', firstname => '', email => '', role => ''};
         }
         if ($a->name eq 'Person Initials' && @persons){
           $persons[-1]->{initials} = $a->value;
         }
         if ($a->name eq 'Person First Name' && @persons){
           $persons[-1]->{firstname} = $a->value;
         }
         if ($a->name eq 'Person Email' && @persons){
           $persons[-1]->{email} = $a->value;
         }
         if ($a->name eq 'Person Role' && @persons){
           $persons[-1]->{role} = $a->value;
         }
      }
      elsif ( $a->name =~ /Term Source/ ) {
        if ($a->name eq 'Term Source Name'){
          push @term_sources,{name => $a->value, uri => '', version => ''};
        }
        if ($a->name eq 'Term Source URI' && @term_sources){
          $term_sources[-1]->{uri} = $a->value;
        }
        if ($a->name eq 'Term Source Version' && @term_sources){
          $term_sources[-1]->{version} = $a->value;
        }
      }
      else {
        $output .= $a->name . $col_sep . $a->value . $line_sep;
      }
    }
  }

  $output .= join($col_sep,'Person Last Name',map {$_->{lastname} || ''} @persons).$line_sep;
  $output .= join($col_sep,'Person Initials',map {$_->{initials} || ''} @persons).$line_sep;
  $output .= join($col_sep,'Person First Name',map {$_->{firstname} || ''} @persons).$line_sep;
  $output .= join($col_sep,'Person Email',map {$_->{email} || ''} @persons).$line_sep;
  $output .= join($col_sep,'Person Role',map {$_->{role} || ''} @persons).$line_sep;

  my @term_sources_used = grep {$self->get_term_source_ref_use($_->{name})} @term_sources;

  $output .= join($col_sep,'Term Source Name',map {$_->{name} || ''} @term_sources_used).$line_sep;
  $output .= join($col_sep,'Term Source URI',map {$_->{uri} || ''} @term_sources_used).$line_sep;
  $output .= join($col_sep,'Term Source Version',map {$_->{version} || ''} @term_sources_used).$line_sep;

  if (!$seen_submission_version){
    $output .= 'Submission Version'.$col_sep.'1.2'.$line_sep;
  }
  if (!$seen_submission_ref_layer){
    $output .= 'Submission Reference Layer'.$col_sep.'false'.$line_sep;
  }
  $output .= $line_sep;
}

sub report_scd {
  my ($self) = @_;

  my $scd_entities      = $self->scd;
  my $reporter          = Bio::Metadata::Reporter::BasicReporter->new();
  my $attribute_columns = $reporter->determine_attr_columns($scd_entities);

  my @output_rows = ( ['[SCD]'] );
  push @output_rows, $self->generate_header($attribute_columns);

  #for each sample
  for my $e (@$scd_entities) {
    my @row = ( $e->id );
    push @output_rows, \@row;

    my $organised_attr = $e->organised_attr;

    #for each possible attribute

    for my $ac (@$attribute_columns) {
      my $attrs = $organised_attr->{ $ac->name };

      #for each possible occurance of that attribute
      for ( my $i = 0 ; $i < $ac->max_count ; $i++ ) {
        my $a;
        if ( $attrs && $i < scalar(@$attrs) && $attrs->[$i] ) {
          $a = $attrs->[$i];
        }
        if ($a) {
          my $id = $a->id // '';
          $id = clean_ids_for_biosamples($id) if $id;
          
          push @row, $a->value      // '';
          push @row, $a->units      // '' if ( $ac->use_units );
          push @row, $a->source_ref // '' if ( $ac->use_source_ref );
          push @row, $id         // '' if ( $ac->use_id );
          push @row, $a->uri        // '' if ( $ac->use_uri );
        }
        else {
          push @row, '';
          push @row, '' if ( $ac->use_units );
          push @row, '' if ( $ac->use_source_ref );
          push @row, '' if ( $ac->use_id );
          push @row, '' if ( $ac->use_uri );
        }
      }
    }
  }
  my $col_sep  = "\t";
  my $line_sep = "\n";

  return join $line_sep, map { join( $col_sep, @$_ ) } @output_rows;
}

sub clean_ids_for_biosamples {
  my ($id) = @_;
  my $nid = $id;
  #we use NCBITaxon when validating, but BioSamples just want the numeric
  if ($nid =~ m/^NCBITaxon_\d+/){
    $nid =~ s/^NCBITaxon_//;
  }
  #ols allows : in id when we validate, but BioSamples will just stick it on the end of the URL to get a term URI
  elsif ($nid =~ m/[A-Za-z]+:\d+/) {
    $nid =~ s/:/_/;
  }
  
  return $nid;
}

sub generate_header {
  my ( $self, $attribute_columns ) = @_;
  my @row = ('Sample Name');

  my $organised_rules = $self->rule_set ? $self->rule_set->organised_rules : {};

  for my $ac (@$attribute_columns) {

    for ( my $i = 0 ; $i < $ac->max_count ; $i++ ) {
      my $rules = $organised_rules->{ $ac->name };
      my $name = $rules ? $rules->[0]->name : $ac->name;
      if ( !exists $named{$name} && !exists $relationships{$name} ) {
        $name = "Characteristic[$name]";
      }
      push @row, $name;
      push @row, 'Unit' if ( $ac->use_units );
      push @row, 'Term Source REF' if ( $ac->use_source_ref );
      push @row, 'Term Source ID' if ( $ac->use_id );
      push @row, 'Term Source URI' if ( $ac->use_uri );
    }
  }
  return \@row;
}

1;
