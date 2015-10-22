
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

package Bio::Metadata::Reporter::AttributeColumn;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;

has 'name' => ( is => 'rw', isa => 'Str', required => 1 );
has [ 'use_units', 'use_uri', ] =>
  ( is => 'rw', isa => 'Bool', required => 1, default => '' );
has 'max_count' => (
    is       => 'rw',
    isa      => 'Int',
    required => 1,
    default  => 0,
);

__PACKAGE__->meta->make_immutable;

1;
