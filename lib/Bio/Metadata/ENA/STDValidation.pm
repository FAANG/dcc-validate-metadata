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
package Bio::Metadata::ENA::STDValidation;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Validate::EntityValidator;


has 'study_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'Study XML section - study',
      rule_groups => [
        {
          name  => 'Study rules',
          rules => [
            {
              name      => 'study_alias',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'center_name',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'STUDY_TITLE',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'STUDY_TYPE',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'STUDY_DESCRIPTION',
              mandatory => 'optional',
              type      => 'text'
            },
          ]
        },
      ]
    };
  }
);

sub validate_std {
  my ( $self, $std_entries ) = @_;

  my %blocks;
  for my $std_entity (@$std_entries) {
    $blocks{ $std_entity->id } //= [];
    push @{ $blocks{ $std_entity->id } }, $std_entity;
  }

  my @errors;
  push @errors,
    $self->validate_section( \%blocks, 'study',
    $self->study_rule_set, 1, 0 );

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $block_name, $rule_set, $just_one, $at_least_one ) = @_;

  my $entities = $blocks->{$block_name} || [];

  my $v =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  my @errors;
  for my $e (@$entities) {
    my ( $outcome_overall, $validation_outcomes ) = $v->check($e);
    push @errors, grep { $_->outcome ne 'pass' } @$validation_outcomes;
  }

  return @errors;
}

__PACKAGE__->meta->make_immutable;
1;