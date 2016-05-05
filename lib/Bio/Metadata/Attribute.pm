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
package Bio::Metadata::Attribute;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;

has 'name'       => ( is => 'rw', isa => 'Str' );
has 'value'      => ( is => 'rw', isa => 'Str' );
has 'units'      => ( is => 'rw', isa => 'Str' );
has 'uri'        => ( is => 'rw', isa => 'Str' );
has 'id'         => ( is => 'rw', isa => 'Str' );
has 'source_ref' => ( is => 'rw', isa => 'Str' );

has 'allow_further_validation' => (
    is      => 'rw',
    isa     => 'Bio::Metadata::FlexiBool',
    default => 1,
);

sub block_further_validation {
  my ($self) = @_;
  $self->allow_further_validation(0);
}

sub source_ref_id {
    my ($self) = @_;
    return ( $self->source_ref || $self->id )
      ? join( ':', $self->source_ref // '', $self->id // '' )
      : '';
}

sub to_hash {
    my ($self) = @_;

    return {
        name       => $self->name,
        value      => $self->value,
        units      => $self->units,
        uri        => $self->uri,
        id         => $self->id,
        source_ref => $self->source_ref,
    };
}

sub TO_JSON { return { %{ shift() } }; }

__PACKAGE__->meta->make_immutable;

1;
