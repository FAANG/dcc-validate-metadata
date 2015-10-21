
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

package Bio::Metadata::Validate::EnumAttributeValidator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Validate::ValidationOutcome;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !$attribute->value ) {
        $o->outcome('error');
        $o->message('no value provided');
    }
    elsif ( !$rule->find_valid_value( sub {$attribute->value eq $_} ) ) {
        $o->outcome('error');
        $o->message( 'value is not in list of valid values:'
              . $rule->join_valid_values(',') );
    }
    else {
        $o->outcome('pass');
    }

    return $o;
}

1;
