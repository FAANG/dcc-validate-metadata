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

  my $output;
  $output .= "[MSI]\n";

  my ( $name, $uri, $version );
  foreach my $e ( @{ $self->msi } ) {
    my $atts = $e->attributes;
    foreach my $a (@$atts) {
      next if !$a->value;
      if ( $a->name =~ /Term Source/ ) {
        $name    .= $a->value . "\t" if $a->name eq 'Term Source Name';
        $uri     .= $a->value . "\t" if $a->name eq 'Term Source URI';
        $version .= $a->value . "\t" if $a->name eq 'Term Source Version';
      }
      else {
        $output .= $a->name . "\t" . $a->value . "\n";
      }

    }
  }
  $output .= "Term Source Name\t$name\n"       if defined $name;
  $output .= "Term Source URI\t$uri\n"         if defined $uri;
  $output .= "Term Source Version\t$version\n" if defined $version;
  $output .= "\n";
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

  for my $ac (@$attribute_columns) {
    for ( my $i = 0 ; $i < $ac->max_count ; $i++ ) {
      my $name = $ac->name;
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
