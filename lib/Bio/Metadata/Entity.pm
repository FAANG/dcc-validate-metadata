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
package Bio::Metadata::Entity;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Metadata::Attribute;
use Bio::Validate::Types;



has 'id'          => ( is => 'rw', isa => 'Str' );
has 'entity_type' => ( is => 'rw', isa => 'Str' );
has 'attributes'  => (
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
    coerce => 1,
);

sub to_hash {
    my ($self) = @_;

    my @attr = map { $_->to_hash } $self->all_attributes;

    return {
        id          => $self->id,
        entity_type => $self->entity_type,
        attributes  => \@attr,
    };
}

1;