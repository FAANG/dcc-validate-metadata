
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

package Bio::Metadata::Validate::Validator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Metadata::Types;
use Bio::Metadata::Validate::ValidatioOutcome;
use Bio::Metadata::Entity;

has 'rule_set' =>
  ( is => 'rw', isa => 'Bio::Metadata::Rules::RuleSet', required => 1 );

sub check {
    my ( $self, $entity ) = @_;

    my @outcomes;

}
