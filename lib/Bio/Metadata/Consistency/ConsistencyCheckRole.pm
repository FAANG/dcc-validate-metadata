
=head1 LICENSE
   Copyright 2016 EMBL - European Bioinformatics Institute
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

package Bio::Metadata::Consistency::ConsistencyCheckRole;

use strict;
use warnings;

use Carp;
use Moose::Role;

use Data::Dumper;
use MooseX::Params::Validate;

requires 'check_entity';
requires 'description';

around 'check_entity' => sub {
  my $orig = shift;
  my $self = shift;
  my ( $entity, $entities_by_id ) = pos_validated_list(
    \@_,
    { isa => 'Bio::Metadata::Entity' },
    { isa => 'HashRef[Bio::Metadata::Entity]' },
  );

  my @returned = $self->$orig( $entity, $entities_by_id );

  my ($outcomes) =
    pos_validated_list( \@returned,
    { isa => 'ArrayRef[Bio::Metadata::Validate::ValidationOutcome]' },
    );

  return @returned;
};

around 'description' => sub {
  my $orig = shift;
  my $self = shift;

  my @returned = $self->$orig();

  my ($desc) =
    pos_validated_list( \@returned,
    { isa => 'Str' },
    );

  return @returned;
};

1;
