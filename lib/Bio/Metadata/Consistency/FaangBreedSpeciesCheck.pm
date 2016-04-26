
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

package Bio::Metadata::Consistency::FaangBreedSpeciesCheck;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;

use Bio::Metadata::Validate::Support::OlsLookup;

has description => (
  is => 'rw',
  isa => 'Str',
  default => 'Check that the animal breed is consistent with it\'s species.',
);

#must consume after declaring attribute that satisfies a requirement
with 'Bio::Metadata::Consistency::ConsistencyCheckRole';

has ols_lookup => (
    is      => 'rw',
    isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
    default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

sub check_entity {
  my ($self, $entity, $entities_by_id ) = @_;
  my @outcomes;



  return \@outcomes;
}

__PACKAGE__->meta->make_immutable;

1;
