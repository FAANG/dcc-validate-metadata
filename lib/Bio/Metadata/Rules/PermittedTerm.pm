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
package Bio::Metadata::Rules::PermittedTerm;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use Bio::Metadata::Rules::Rule;
use MooseX::Types::URI qw(Uri);

has 'ontology_name'     => ( is => 'rw', isa => 'Str' );
has 'allow_descendants' => ( is => 'rw', isa => 'Bool', default => 1 );
has 'leaf_only'         => ( is => 'rw', isa => 'Bool', default => 0 );
has 'include_root'      => ( is => 'rw', isa => 'Bool', default => 1 );

has 'term_iri' => ( is => 'rw', isa => Uri, required => 1, coerce => 1 );

sub to_hash {
  my ($self) = @_;

  return {
    ontology_name     => $self->ontology_name,
    term_iri          => $self->term_iri->as_string,
    allow_descendants => $self->allow_descendants,
    leaf_only         => $self->leaf_only ? 1 : 0,
    include_root      => $self->include_root ? 1 : 0,
  };
}

__PACKAGE__->meta->make_immutable;
1;
