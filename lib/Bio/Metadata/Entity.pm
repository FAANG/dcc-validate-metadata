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
use JSON;
use namespace::autoclean;
use Unicode::CaseFold;

use Bio::Metadata::Attribute;
use Bio::Metadata::Types;

has 'id'          => ( is => 'rw', isa => 'Str' );
has 'entity_type' => ( is => 'rw', isa => 'Str' );
has 'links'       => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_links   => 'elements',
    add_link    => 'push',
    count_links => 'count',
    get_link    => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);
has 'attributes' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::AttributeArrayRef',
  handles => {
    all_attributes   => 'elements',
    add_attribute    => 'push',
    count_attributes => 'count',
    get_attribute    => 'get',
    find_attribute   => 'first',
  },
  default => sub { [] },
  coerce  => 1,
);

sub to_hash {
  my ($self) = @_;

  my @attr  = map { $_->to_hash } $self->all_attributes;
  my @links = map { $_->to_hash } $self->all_links;

  return {
    id          => $self->id,
    entity_type => $self->entity_type,
    attributes  => \@attr,
    links       => \@links,
  };
}

sub normalise_attribute_name {
  my ( $self, $name ) = @_;
  return fc $name;
}

sub organised_attr {
  my ($self, $preserve_case) = @_;

  my %h;

  for my $a ( $self->all_attributes ) {
    next if ( !$a->name || !defined $a->value || $a->value eq '' );
    my $name = $preserve_case ? $a->name : $self->normalise_attribute_name( $a->name );
    $h{$name} //= [];
    push @{ $h{$name} }, $a;
  }
  return \%h;
}

sub attr_names {
  my ($self) = @_;

  my %names_seen;
  my @names =
    grep { !$names_seen{$_}++ }
    map  { $self->normalise_attribute_name( $_->name ) } @{ $self->attributes };
  return \@names;
}

sub TO_JSON { return { %{ shift() } }; }

sub to_json_tmp {
  my ($self) = @_;

  my $JSON = JSON->new->utf8;
  $JSON->convert_blessed(1);

  my $json_text = $JSON->pretty->encode($self);

  return $json_text;
}

__PACKAGE__->meta->make_immutable;

1;
