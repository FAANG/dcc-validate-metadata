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
package Bio::Metadata::ValidateSchema::ValidationOutcomeSet;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

has 'outcomes'       => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'Bio::Metadata::ValidateSchema::ValidationOutcomeArrayRef',
    handles => {
        all_outcomes   => 'elements',
        add_outcome    => 'push',
        count_outcomes => 'count',
        get_outcome    => 'get',
    },
    default => sub { [] },
    coerce  => 1,
);


1;
