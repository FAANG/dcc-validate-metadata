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
use Bio::Metadata::ENA::STDValidation;
use Bio::Metadata::ENA::EXPRValidation;
use Bio::Metadata::ENA::RUNValidation;
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
    all_scd   => 'elements',
    add_scd   => 'push',
    count_scd => 'count',
    get_scd   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'std' => (
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

has 'expr' => (
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

has 'run' => (
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

has 'sub_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::SUBValidation',
  default => sub { Bio::Metadata::ENA::SUBValidation->new },
);

has 'std_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::STDValidation',
  default => sub { Bio::Metadata::ENA::STDValidation->new },
);

has 'expr_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::EXPRValidation',
  default => sub { Bio::Metadata::ENA::EXPRValidation->new },
);

has 'run_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::RUNValidation',
  default => sub { Bio::Metadata::ENA::RUNValidation->new },
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

sub read {
  my ( $self, $file_path ) = @_;

  die("[ERROR] Please provide the path to a XLSX file") if !$file_path;

  my $loader = Bio::Metadata::Loader::XLSXExperimentLoader->new();

  $self->sub( $loader->load_sub_entities($file_path) );
  $self->std( $loader->load_std_entities($file_path) );
  $self->exprena( $loader->load_exprena_entities($file_path) );
  $self->exprfaang( $loader->load_exprfaang_entities($file_path) );
  $self->run( $loader->load_run_entities($file_path) );
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
  my $sub_errors = $self->sub_validator->validate_sub( $self->sub );
  my $std_errors = $self->std_validator->validate_std( $self->std );
  my $expr_errors = $self->expr_validator->validate_expr( $self->expr );
  my $run_errors = $self->run_validator->validate_run( $self->run );
  my $subref_errors =
    $self->sub_validator->check_term_source_refs( $self->sub);
  my $stdref_errors =
    $self->std_validator->check_term_source_refs( $self->std);
  my $exprref_errors =
    $self->expr_validator->check_term_source_refs( $self->expr);
  my $runref_errors =
    $self->run_validator->check_term_source_refs( $self->run);
  push @$sub_errors, @$std_errors, @$expr_errors, @$run_errors, 
  @$subref_errors, @$stdref_errors, @$exprref_errors, @$runref_errors;
  return $sub_errors;
}

sub report_sub {
  my ($self) = @_;
  
}

sub report_std {
  my ($self) = @_;

}

sub report_expr {
  my ($self) = @_;

}

sub report_run {
  my ($self) = @_;

}