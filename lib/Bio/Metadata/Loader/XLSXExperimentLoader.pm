
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

package Bio::Metadata::Loader::XLSXExperimentLoader;

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

my $xlsxfilepath;

with "Bio::Metadata::Loader::XLSXLoaderRole" => {
  -alias    => { load => '_load', expand => '_expand',},
  -excludes => ['load', 'expand'],
};

has 'sub_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_sub_sheet_names => 'elements',
    find_sub_sheet_name => 'first',
  },
  default => sub { [ 'Submission' ] },
);

has 'std_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_stud_sheet_names => 'elements',
    find_stud_sheet_name => 'first',
  },
  default => sub { [ 'Study' ] },
);

has 'exprena_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_exprena_sheet_names => 'elements',
    find_exprena_sheet_name => 'first',
  },
  default => sub { [ 
  'Experiment_ENA'
  ] },
);

has 'exprfaang_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_exprfaang_sheet_names => 'elements',
    find_exprfaang_sheet_name => 'first',
  },
  default => sub { [ 
  'Experiment_FAANG'
  ] },
);

has 'expr_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_expr_sheet_names => 'elements',
    find_expr_sheet_name => 'first',
  },
  default => sub { [ 
  'ATAC-seq', 'BS-seq', 'ChIP-seq', 'ChIP-seq histone modifications', 'ChIP-seq input',
  'DNase-seq', 'HiC', 'RNA-Seq', 'WGS'
  ] },
);

has 'run_sheet_names' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'ArrayRef[Str]',
  handles => {
    all_run_sheet_names => 'elements',
    find_run_sheet_name => 'first',
  },
  default => sub {
    ['Run']
  },
);

sub load_std_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->std_sheet_names );
}
sub load_sub_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->sub_sheet_names );
}
sub load_run_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->run_sheet_names );
}
sub expand_expr_entities {
  my ( $self, $file_path, $entities ) = @_;
  return $self->_expand( $file_path, $self->expr_sheet_names, $entities );
}
sub load_exprena_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->exprena_sheet_names );
}
sub load_exprfaang_entities {
  my ( $self, $file_path ) = @_;
  return $self->_load( $file_path, $self->exprfaang_sheet_names );
}

sub load {
  my ( $self, $file_path ) = @_;
  $xlsxfilepath = $file_path;
  return $self->load_exprfaang_entities($file_path);
}

sub process_sheet {
  my ( $self, $sheet ) = @_;

  if ( !$self->find_stud_sheet_name( sub { $_ eq $sheet->get_name } )
    && !$self->find_sub_sheet_name( sub { $_ eq $sheet->get_name } )
    && !$self->find_run_sheet_name( sub { $_ eq $sheet->get_name } )
    && !$self->find_exprfaang_sheet_name( sub { $_ eq $sheet->get_name } )
    && !$self->find_exprena_sheet_name( sub { $_ eq $sheet->get_name } ) )
  {
    carp( "[WARN] refusing to process worksheet with unexpected name: "
        . $sheet->name );
    return 0;
  }

  my ( $row_min, $row_max ) = $sheet->row_range;
  my ( $col_min, $col_max ) = $sheet->col_range;

  my @fields;
  my @entities;
  my %expr_entities;

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
      if ( $self->find_exprfaang_sheet_name( sub { $_ eq $sheet->get_name } )){
        ($expr_entities{$e->id} = $e) if $e;
      }else{
        push @entities, $e if $e;
      }
    }
    else {
      @fields = @row;
    }
  }
  if ( $self->find_exprfaang_sheet_name( sub { $_ eq $sheet->get_name } ) ){
    #Add extra info to entities
    my $expanded_expr_entities = $self->expand_expr_entities($xlsxfilepath, \%expr_entities);
    #Convert hash of entities to array of entities
    foreach my $key (keys %$expanded_expr_entities){
      push(@entities, $$expanded_expr_entities{$key});
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
  if ( $self->find_stud_sheet_name( sub { $_ eq $sheet_name } ) ) {  
    $o->id( $sheet_name );
    $o->entity_type('Study');
  }elsif ( $self->find_sub_sheet_name( sub { $_ eq $sheet_name } ) ) {
    $o->id( $sheet_name );
    $o->entity_type('Submission');
  }elsif ( $self->find_run_sheet_name( sub { $_ eq $sheet_name } ) ) {
    $o->id( $row->[0] );
    $o->entity_type('Run');
  }elsif ( $self->find_exprena_sheet_name( sub { $_ eq $sheet_name } ) ) {
    $o->id( $row->[1] );
    $o->entity_type('Experiment_ENA');
    my $sample_id=$row->[0];
    my $sample = Bio::Metadata::Entity->new(
            id          => $sample_id,
            entity_type => 'sample');
    $o->add_link($sample);
    my $study_id=$row->[4];
    my $study = Bio::Metadata::Entity->new(
          id          => $study_id,
          entity_type => 'study');
    $o->add_link($study);
  }elsif ( $self->find_exprfaang_sheet_name( sub { $_ eq $sheet_name } ) ) {     
    $index = 2;
    $o->id( $row->[1] );
    $o->entity_type('experiment');
    #set 'links' in Entity.pm
    my $sample_id=$row->[0];
    my $sample = Bio::Metadata::Entity->new(
            id          => $sample_id,
            entity_type => 'sample');
    $o->add_link($sample);
  }
  #read through lines in each Excel sheet
  #save into attributes list
  #each attribute could have keywords name, value, id (ontology id), source_ref (ontology library) and units
  #$pr_att save the previous processed attribute, the purpose of which is to allow reading in the ontology information provided in the excel
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

sub process_expansion_sheet{
  my ( $self, $sheet, $entities ) = @_;
  if ( !$self->find_expr_sheet_name( sub { $_ eq $sheet->get_name } ))
  {
    carp( "[WARN] refusing to process worksheet with unexpected name: "
        . $sheet->name );
    return 0;
  }

  my ( $row_min, $row_max ) = $sheet->row_range;
  my ( $col_min, $col_max ) = $sheet->col_range;

  my @fields;
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
      $entities = $self->row_to_object_expand( \@row, \@fields, $sheet->get_name, $entities );
    }else {
      @fields = @row;
    }

  }
  return $entities;
}

sub row_to_object_expand {
  my ( $self, $row, $fields, $sheet_name, $entities ) = @_;
  return $entities unless grep { $_ } @$row;

  croak("[ERROR] Number of fields in the header/rows does not match")
    if scalar(@$fields) != scalar(@$row);

  my $index = 2;
  if ( $self->find_expr_sheet_name( sub { $_ eq $sheet_name } )) {
    my $o = $$entities{$row->[1]};
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
    $$entities{$row->[1]}=$o;
  }
  return $entities;
}

__PACKAGE__->meta->make_immutable;
1;
