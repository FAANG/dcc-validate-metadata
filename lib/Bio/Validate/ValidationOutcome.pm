
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

package Bio::Validate::ValidationOutcome;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Validate::Types;
use Bio::Metadata::Attribute;
use Bio::Metadata::Entity;

has 'rule'       => ( is => 'rw', isa => 'Bio::Rules::Rule' );
has 'rule_group' => ( is => 'rw', isa => 'Bio::Rules::RuleGroup' );

has 'outcome' => ( is => 'rw', isa => 'Bio::Validate::OutcomeEnum' );
has 'message' => ( is => 'rw', isa => 'Str' );

has 'entity' => ( is => 'rw', isa => 'Bio::Metadata::Entity' );
has 'attributes' => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'Bio::Metadata::AttributeArrayRef',
    handles => {
        all_attributes   => 'elements',
        add_attribute    => 'push',
        count_attributes => 'count',
        get_attribute    => 'get',
    },
    default => sub { [] },
    coerce  => 1,
);

sub to_hash {
    my ($self) = @_;

    my @a = map { $_->to_hash } $self->all_attributes;
    return {
        rule            => $self->rule->to_hash,
        rule_group_name => $self->rule_group->name,
        outcome         => $self->outcome,
        message         => $self->message,
        entity_id       => $self->entity->id,
        entity_type     => $self->entity->entity_type,
        attributes      => \@a,
    };
}

1;
