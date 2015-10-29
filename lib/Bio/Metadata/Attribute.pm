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

has 'name'   => ( is => 'rw', isa => 'Str' );
has 'value' => ( is => 'rw', isa => 'Str' );
has 'units' => ( is => 'rw', isa => 'Str' );
has 'uri'   => ( is => 'rw', isa => 'Str' );

sub to_hash {
  my ($self) = @_;
  
  return {
	  name  => $self->name,
	  value => $self->value,
	  units => $self->units,
	  uri   => $self->uri,
	 };
}

sub TO_JSON { return { %{ shift() } }; }

#_PACKAGE__->meta->make_immutable;

1;
