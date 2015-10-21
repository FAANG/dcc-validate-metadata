
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

package Bio::Metadata::Validate::Validator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Metadata::Types;
use Bio::Metadata::Validate::ValidatioOutcome;
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

sub check {
    my ($self) = shift;
    my ($entity) =
      pos_validated_list( \@_, { isa => 'Bio::Metadata::Entity' }, );

    my @all_outcomes;

    my $organised_attributes  = $entity->organised_attr;
    my $requirement_validator = $self->requirement_validator;
    my $unit_validator        = $self->unit_validator;

    for my $rule_group ( $self->rule_set->all_rule_groups ) {


        for my $rule ( $rule_group->all_rules ) {
            my @r_outcomes;
            
            my $type_validator = $self->get_type_validator($rule->type)
            

            my $attrs = $organised_attributes->{ $rule->name } // [];

            push @r_outcomes,
              $requirement_validator->validate_requirements( $rule, $attrs );
            
            for my $a (@$attrs) {
                push @r_outcomes, $unit_validator->validate_attribute($rule,$a)
                  if ( $rule->count_valid_units );
                push @r_outcomes, $type_validator->validate_attribute($rule,$a);
            }
            
            for my $o (@r_outcomes){
              $o->rule($rule);
              $o->rule_group($rule_group);
              $o->entity($entity)
            }
            push @all_outcomes, @r_outcomes;
        }
    }

    return \@outcomes;
}
