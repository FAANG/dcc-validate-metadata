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
package Bio::Metadata::ENA::SUBValidation;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Validate::EntityValidator;

has 'submission_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'Submission XML section - submission',
      rule_groups => [
        {
          name  => 'Submission rules',
          rules => [
            {
              name      => 'alias',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'HoldUntilDate',
              mandatory => 'optional',
              type      => 'text'#TODO Should validate this in ENA data format (this is different to FAANG date format)
            },
          ]
        },
      ]
    };
  }
);

sub validate_sub {
  my ( $self, $sub_entries ) = @_;

  my %blocks;
  for my $sub_entity (@$sub_entries) {
    $blocks{ $sub_entity->id } //= [];
    push @{ $blocks{ $sub_entity->id } }, $sub_entity;
  }

  my @errors;
  push @errors,
    $self->validate_section( \%blocks, 'Submission',
    $self->submission_rule_set);

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $block_name, $rule_set, $just_one) = @_;

  my $entities = $blocks->{$block_name} || [];

  my $v =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  if ( scalar(@$entities) != 1 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "One $block_name block required",
      rule =>
        Bio::Metadata::Rules::Rule->new( name => $block_name, type => 'text' ),
    );
  }

  my @errors;
  for my $e (@$entities) {
    my ( $outcome_overall, $validation_outcomes ) = $v->check($e);
    push @errors, grep { $_->outcome ne 'pass' } @$validation_outcomes;
  }

  return @errors;
}

__PACKAGE__->meta->make_immutable;
1;