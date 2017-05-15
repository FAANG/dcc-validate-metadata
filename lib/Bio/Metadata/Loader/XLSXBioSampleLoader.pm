
=head1 LICENSE
   Copyright 2015 EMBL - European Bioinformatics Institute
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
=cut

package Bio::Metadata::Loader::XLSXBioSampleLoader;

use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Encode::Guess;
use Encode qw(encode decode);
use Moose;
use Carp;
use Data::Dumper;
use namespace::autoclean;
use Bio::Metadata::Entity;
use Text::Unidecode;

with "Bio::Metadata::Loader::XLSXLoaderRole" => {
  -alias    => { load => '_load', },
  -excludes => ['load'],
};

has 'scd_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_scd_sheet_names => 'elements',
    find_scd_sheet_name => 'first',
  },
  default => sub { [ 'animal', 'specimen', 'pool of specimens', 'purified cells', 'cell culture', 'cell line' ] },
);

has 'msi_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_msi_sheet_names => 'elements',
    find_msi_sheet_name => 'first',
  },
  default => sub {
    [
      'submission', 'person', 'organization', 'publication',
      'database',   'term source'
    ];
  },
);

sub load_scd_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->scd_sheet_names );
}

sub load_msi_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->msi_sheet_names );

}

sub load {
  my ( $self, $file_path ) = @_;
  return $self->load_scd_entities($file_path);
}

sub process_sheet {
  my ( $self, $sheet ) = @_;

  if ( !$self->find_scd_sheet_name( sub { $_ eq $sheet->get_name } )
    && !$self->find_msi_sheet_name( sub { $_ eq $sheet->get_name } ) )
  {
    carp( "[WARN] refusing to process worksheet with unexpected name: "
        . $sheet->name );
    return 0;
  }

  my ( $row_min, $row_max ) = $sheet->row_range;
  my ( $col_min, $col_max ) = $sheet->col_range;

  my @fields;
  my @entities;

  for ( my $r = $row_min ; $r <= $row_max ; $r++ ) {
    my @row;
    for ( my $c = $col_min ; $c <= $col_max ; $c++ ) {
      my $cell = $sheet->get_cell( $r, $c );

      my $v = $cell ? $cell->value() : '';
      #get rid of accents etc, nbsp
      $v = unidecode($v);
      $v =~ s/([^[:ascii:]])/ /g;
      #get rid of multiple spaces
      $v =~ s/\s+/ /g;
      #get rid of trailing spaces
      $v =~ s/\s+$//g;
      #get rid of leading spaces
      $v =~ s/^\s+//g;
      push @row, $v;
    }
    if (@fields) {
      my $e = $self->row_to_object( \@row, \@fields, $sheet->get_name );
      push @entities, $e if $e;
    }
    else {
      @fields = @row;
    }
  }
  return \@entities;
}

sub row_to_object {
  my ( $self, $row, $fields, $sheet_name ) = @_;

  return 0 unless grep { $_ } @$row;

  croak("[ERROR] Number of fields in the header/rows does not match")
    if scalar(@$fields) != scalar(@$row);

  my $o = Bio::Metadata::Entity->new();

  my $index = 0;
  if ( $self->find_scd_sheet_name( sub { $_ eq $sheet_name } ) ) {
    $o->id( $row->[0] );
    $o->entity_type('sample');
    $index = 1;
  }
  elsif ( $self->find_msi_sheet_name( sub { $_ eq $sheet_name } ) ) {
    $o->id($sheet_name);
    $o->entity_type('msi');
  }

  my $pr_att;
  for ( my $i = $index ; $i < scalar(@$row) ; $i++ ) {
    my $name = $fields->[$i];

    if ( lc($name) eq 'term source ref' ) {
      $pr_att->source_ref( $row->[$i] );
    }
    elsif ( lc($name) eq 'term source id' ) {
      $pr_att->id( $row->[$i] );
    }
    elsif ( lc($name) eq 'unit' || lc($name) eq 'units' ) {
      $pr_att->units( $row->[$i] );
    }
    else {
      my $o_attrb = Bio::Metadata::Attribute->new(
        name  => $name,
        value => $row->[$i]
      );
      $o->add_attribute($o_attrb);
      $pr_att = $o_attrb;
    }

  }
  return $o;
}

__PACKAGE__->meta->make_immutable;
1;
