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
package Bio::Metadata::BioSample::MSIValidation;

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
      name        => 'SampleTab MSI section - submission',
      rule_groups => [
        {
          name  => 'Submission rules',
          rules => [
            {
              name      => 'Submission Title',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'Submission Description',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'Submission Version',
              mandatory => 'optional',
              type      => 'number',
            },
            {
              name      => 'Submission Update Date',
              mandatory => 'optional',
              type      => 'text',
            },
            {
              name      => 'Submission Release Date',
              mandatory => 'optional',
              type      => 'text',
            },
            {
              name         => 'Submission Reference Layer',
              mandatory    => 'optional',
              type         => 'text',
              valid_values => ['false'],
            },
            {
              name      => 'Submission Identifier',
              mandatory => 'optional',
              type      => 'text',
            }
          ],
        },
      ],
    };
  },
);

has 'person_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'SampleTab MSI section - person',
      rule_groups => [
        {
          name  => 'Person rules',
          rules => [
            {
              name      => 'Person Last Name',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'Person Initials',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'Person First Name',
              mandatory => 'optional',
              type      => 'text'
            },
            { name => 'Person Email', mandatory => 'optional', type => 'text' },
            {
              name                => 'Person Role',
              mandatory           => 'optional',
              type                => 'ontology_text',
              valid_ancestor_uris => ['http://www.ebi.ac.uk/efo/EFO_0002012']
            },
          ]
        },
      ],
    },
      ;
  }
);

has 'organisation_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'SampleTab MSI section - organization',
      rule_groups => [
        {
          name  => 'Organization rules',
          rules => [
            {
              name      => 'Organization Name',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'Organization Address',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'Organization URI',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name                => 'Organization Role',
              mandatory           => 'optional',
              type                => 'ontology_text',
              valid_ancestor_uris => ['http://www.ebi.ac.uk/efo/EFO_0002012']
            },
          ]
        }
      ]
    };
  }
);

has 'term_source_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'SampleTab MSI section - term source',
      rule_groups => [
        {
          name  => 'Term source rules',
          rules => [
            {
              name      => 'Term Source Name',
              mandatory => 'mandatory',
              type      => 'text',
            },
            {
              name      => 'Term Source URI',
              mandatory => 'mandatory',
              type      => 'uri_value',
            },
            {
              name      => 'Term Source Version',
              mandatory => 'optional',
              type      => 'text',
            },
          ]
        },
      ]
    };
  }
);

has 'database_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'SampleTab MSI section - database',
      rule_groups => [
        {
          name  => 'Database rules',
          rules => [
            {
              name      => 'Database Name',
              mandatory => 'mandatory',
              type      => 'text',
            },
            {
              name      => 'Database ID',
              mandatory => 'optional',
              type      => 'text',
            },
            {
              name      => 'Database URI',
              mandatory => 'optional',
              type      => 'uri_value',
            },
          ]
        },
      ]
    };
  }
);

has 'publication_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'SampleTab MSI section - publication',
      rule_groups => [
        {
          name  => 'Publication rules',
          rules => [
            {
              name      => 'Publication PubMed ID',
              mandatory => 'optional',
              type      => 'number',
            },
            {
              name      => 'Publication DOI',
              mandatory => 'optional',
              type      => 'uri_value',
            },
          ]
        },
      ]
    };
  }
);

sub validate_msi {
  my ( $self, $msi_entries ) = @_;

  my %blocks;
  for my $msi_entity (@$msi_entries) {
    $blocks{ $msi_entity->id } //= [];
    push @{ $blocks{ $msi_entity->id } }, $msi_entity;
  }
  my @errors;
  push @errors,
    $self->validate_section( \%blocks, 'submission',
    $self->submission_rule_set, 1, 0 );
  push @errors,
    $self->validate_section( \%blocks, 'person', $self->person_rule_set, 0, 1 );
  push @errors,
    $self->validate_section( \%blocks, 'organization',
    $self->organisation_rule_set,
    0, 1 );
  push @errors,
    $self->validate_section( \%blocks, 'term source',
    $self->term_source_rule_set, 0, 0 );
  push @errors,
    $self->validate_section( \%blocks, 'database',
    $self->database_rule_set, 0, 0 );
  push @errors,
    $self->validate_section( \%blocks, 'publication',
    $self->publication_rule_set, 0, 0 );

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $block_name, $rule_set, $just_one, $at_least_one ) = @_;

  my $entities = $blocks->{$block_name} || [];

  if ( $just_one && scalar(@$entities) != 1 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "One $block_name block required",
      rule    => Bio::Metadata::Rules::Rule->new( name => $block_name, type => 'text' ),
    );
  }
  if ( $at_least_one && scalar(@$entities) == 0 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "At least one $block_name required",
      rule    => Bio::Metadata::Rules::Rule->new( name => $block_name, type => 'text' ),
    );
  }

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
