
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

package Bio::Metadata::Faang::FaangBreed;

use Moose;
use namespace::autoclean;

has ['sire', 'dam'] => (is => 'rw', isa => 'Str|Bio::Metadata::Faang::FaangBreed');
has 'breeds' => (
  is => 'rw', isa => 'ArrayRef[Str]', traits => ['Array'], handles => {
    'add_breed' => 'push',
  }
);

sub all_breeds {
  my ($self) = @_;

  my @breeds;
  push @breeds, @{$self->breeds} if ($self->breeds);

  for my $x ($self->sire,$self->dam){
    next unless $x;
    if (ref $x){
      push @breeds, $x->all_breeds;
    }
    else {
      push @breeds, $x;
    }
  }

  return @breeds;
}



__PACKAGE__->meta->make_immutable;
1;
