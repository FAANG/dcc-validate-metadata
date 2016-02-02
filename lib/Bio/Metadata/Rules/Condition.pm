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
package Bio::Metadata::Rules::Condition;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use MooseX::Params::Validate;

use Data::DPath 'dpath';

has 'dpath_condition' => ( is => 'rw', isa => 'Str' );
has 'attribute_value_match' => (
    is      => 'rw',
    isa     => 'HashRef[ArrayRef[Str]]',
    traits  => ['Hash'],
    handles => {
        attribute_value_match_keys  => 'keys',
        get_attribute_value_match   => 'get',
        num_attribute_value_matches => 'count',
    },
);

sub entity_passes {
    my $self = shift;
    my ($entity) =
      pos_validated_list( \@_, { isa => 'Bio::Metadata::Entity' }, );

    my $pass = 1;
    if ( $self->num_attribute_value_matches ) {
        $pass = $self->check_attribute_condition($entity);
    }

    if ( $pass && $self->dpath_condition ) {
        $pass = $self->check_dpath_condition($entity);
    }

    return $pass;

}

sub check_dpath_condition {
    my ( $self, $entity ) = @_;
    
    my $match = dpath( $self->dpath_condition )->match( $entity->to_hash );

    return $match;

}

sub check_attribute_condition {
    my ( $self, $entity ) = @_;

    my $attr_match_count = 0;
    for my $attribute ( $self->attribute_value_match_keys ) {
        my %match_values;
        map { $match_values{$_}++ }
          ( @{ $self->get_attribute_value_match($attribute) } );

        my $match =
          $entity->find_attribute(
            sub {  $_->name eq $attribute && $match_values{ $_->value } } );
        if ($match) {
            ++$attr_match_count;
        }

    }

    return ( $attr_match_count == $self->num_attribute_value_matches );
}

__PACKAGE__->meta->make_immutable;
1;
