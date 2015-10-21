
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

package Bio::Metadata::Loader::EntityLoader;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use Bio::Metadata::Entity;

with "Bio::Metadata::Loader::LoaderRole";

sub hash_to_object {
    my ( $self, $hash ) = @_;

    my $o = Bio::Metadata::Entity->new($hash); 

    return $o;
}

__PACKAGE__->meta->make_immutable;
1;
