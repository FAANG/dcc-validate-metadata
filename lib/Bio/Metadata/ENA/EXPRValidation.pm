# Copyright 2016 European Molecular Biology Laboratory - European Bioinformatics Institute
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
package Bio::Metadata::ENA::EXPRValidation;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Validate::EntityValidator;

has 'ena_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'ENA XML section - ena',
      rule_groups => [
        {
          name  => 'ENA rules',
          rules => [
            {
              name      => 'SAMPLE_DESCRIPTOR',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'EXPERIMENT_alias',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'TITLE',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'STUDY_REF',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'DESIGN_DESCRIPTION',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_NAME',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_STRATEGY',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_SOURCE',
              mandatory => 'mandatory',
              type      => 'text'
            },
                        {
              name      => 'LIBRARY_SELECTION',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_LAYOUT',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'NOMINAL_LENGTH',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'NOMINAL_SDEV',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_CONSTRUCTION_PROTOCOL',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'PLATFORM',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'INSTRUMENT_MODEL',
              mandatory => 'optional',
              type      => 'text'
            },
          ]
        },
      ]
    };
  }
);

sub validate_expr {
  my ( $self, $expr_entries ) = @_;

  my %blocks;
  for my $expr_entity (@$expr_entries) {
    $blocks{ $expr_entity->id } //= [];
    push @{ $blocks{ $expr_entity->id } }, $expr_entity;
  }

  my @errors;
  push @errors,
    $self->validate_section( \%blocks, $self->ena_rule_set);

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $rule_set) = @_;

  my @rows = keys(%$blocks);

  if ( scalar(@rows) == 0 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "At least one ENA experiment row required",
      rule =>
        Bio::Metadata::Rules::Rule->new( name => "experiment_ena", type => 'text' ),
    );
  }

  my $v = Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  my @errors;
  foreach my $row (@rows){
    my $entities = $blocks->{$row} || [];
    for my $e (@$entities) {
      my ( $outcome_overall, $validation_outcomes ) = $v->check($e);
      push @errors, grep { $_->outcome ne 'pass' } @$validation_outcomes;
    }
  }
  return @errors;
}

__PACKAGE__->meta->make_immutable;
1;