
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

package Bio::Metadata::Validate::EntityValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;

use Data::DPath 'dpath';
use Data::Dumper;

use Bio::Metadata::Types;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Entity;

use MooseX::Params::Validate;
use Bio::Metadata::Validate::RequirementValidator;
use Bio::Metadata::Validate::UnitAttributeValidator;
use Bio::Metadata::Validate::TextAttributeValidator;
use Bio::Metadata::Validate::NumberAttributeValidator;
use Bio::Metadata::Validate::EnumAttributeValidator;

has 'rule_set' =>
  ( is => 'rw', isa => 'Bio::Metadata::Rules::RuleSet', required => 1 );
has 'requirement_validator' => (
    is       => 'rw',
    isa      => 'Bio::Metadata::Validate::RequirementValidator',
    required => 1,
    default  => sub { Bio::Metadata::Validate::RequirementValidator->new() }
);
has 'unit_validator' => (
    is       => 'rw',
    isa      => 'Bio::Metadata::Validate::UnitAttributeValidator',
    required => 1,
    default  => sub { Bio::Metadata::Validate::UnitAttributeValidator->new() }
);
has 'type_validator' => (
    traits   => ['Hash'],
    is       => 'rw',
    isa      => 'HashRef[Bio::Metadata::Validate::AttributeValidatorRole]',
    required => 1,
    handles  => { get_type_validator => 'get', },
    default  => sub {
        {
            text   => Bio::Metadata::Validate::TextAttributeValidator->new(),
            number => Bio::Metadata::Validate::NumberAttributeValidator->new(),
            enum   => Bio::Metadata::Validate::EnumAttributeValidator->new(),
        };
    },
);
has 'outcome_for_unexpected_attributes' => (
    is       => 'rw',
    isa      => 'Bio::Metadata::Validate::OutcomeEnum',
    required => 1,
    default  => sub { 'warning' },
);
has 'message_for_unexpected_attributes' => (
    is       => 'rw',
    isa      => 'Str',
    required => 1,
    default  => sub { 'attribute not in rule set' },
);

sub check {
    my ($self,$entity) = @_;

    my @all_outcomes;

    my $organised_attributes  = $entity->organised_attr;
    my $requirement_validator = $self->requirement_validator;
    my $unit_validator        = $self->unit_validator;

    my $entity_as_hash = $entity->to_hash;

    
  RULE_GROUP: for my $rule_group ( $self->rule_set->all_rule_groups ) {

        if ( $rule_group->condition ) {

            my $match_count = dpath($rule_group->condition)->match($entity_as_hash);

            if ( !$match_count ) {
                next RULE_GROUP;
            }
        }


        for my $rule ( $rule_group->all_rules ) {
            my @r_outcomes;
            
            my $type_validator = $self->get_type_validator( $rule->type );
            croak( "No type validator for " . $rule->type )
              if ( !$type_validator );

            my $attrs = $organised_attributes->{ $rule->name } // [];
            delete $organised_attributes->{ $rule->name };

            push @r_outcomes,
              $requirement_validator->validate_requirements( $rule, $attrs );

            for my $a (@$attrs) {
                if ( $rule->count_valid_units ) {
                    push @r_outcomes,
                      $unit_validator->validate_attribute( $rule, $a );
                }
                push @r_outcomes,
                  $type_validator->validate_attribute( $rule, $a );
            }

            for my $o (@r_outcomes) {
                $o->rule_group($rule_group);
                $o->entity($entity);
            }
            push @all_outcomes, grep { $_->outcome ne 'pass' } @r_outcomes;
        }
    }

    for my $unexpected_attributes ( values %$organised_attributes ) {
        push @all_outcomes,
          Bio::Metadata::Validate::ValidationOutcome->new(
            attributes => $unexpected_attributes,
            entity     => $entity,
            outcome    => $self->outcome_for_unexpected_attributes,
            message    => $self->message_for_unexpected_attributes,
          );
    }

    my $outcome_overall = 'pass';
    for my $o (@all_outcomes) {
        if ( $o->outcome eq 'error' ) {
            $outcome_overall = 'error';
            last;
        }
        if ( $o->outcome eq 'warning' ) {
            $outcome_overall = 'warning';
        }
    }

    return pos_validated_list(
        [ $outcome_overall, \@all_outcomes ],
        { isa => 'Bio::Metadata::Validate::OutcomeEnum' },
        { isa => 'Bio::Metadata::Validate::ValidationOutcomeArrayRef' }
    );
}

__PACKAGE__->meta->make_immutable;

1;
