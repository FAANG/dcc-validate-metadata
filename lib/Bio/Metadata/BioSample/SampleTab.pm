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

  my $output ="[MSI]$/";
  my $sep = "\t";

  my @term_sources;

  for my $e ( $self->all_msi ) {
    for my $a ($e->all_attributes) {

      next if ! defined $a->value;

      if ( $a->name =~ /Term Source/ ) {
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
        $output .= $a->name . $sep . $a->value . $/;
      }
    }
  }

  my @term_sources_used = grep {$self->get_term_source_ref_use($_->{name})} @term_sources;

  $output .= join($sep,'Term Source Name',map {$_->{name} || ''} @term_sources_used).$/;
  $output .= join($sep,'Term Source URI',map {$_->{uri} || ''} @term_sources_used).$/;
  $output .= join($sep,'Term Source Version',map {$_->{version} || ''} @term_sources_used).$/;
  $output .= $/;
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
          push @row, $a->value      // '';
          push @row, $a->units      // '' if ( $ac->use_units );
          push @row, $a->source_ref // '' if ( $ac->use_source_ref );
          push @row, $a->id         // '' if ( $ac->use_id );
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
