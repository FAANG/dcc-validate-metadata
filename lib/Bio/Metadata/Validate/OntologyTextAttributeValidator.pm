
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

package Bio::Metadata::Validate::OntologyTextAttributeValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use Try::Tiny;

use Bio::Metadata::Validate::Support::OlsLookup;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'ols_lookup' => (
    is      => 'rw',
    isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
    default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !$attribute->value ) {
        $o->outcome('error');
        $o->message('value required');
        return $o;
    }

    my $match;
  ANCESTOR: for my $valid_term ( $rule->all_valid_terms ) {
        $match =
          $self->ols_lookup->find_match_all_children( $attribute->value, $valid_term, 1 );
        if ($match) {
            last ANCESTOR;
        }
    }

    if ( !$match ) {
        $o->outcome('error');
        $o->message('value ('.$attribute->value.') is not a valid term');
        return $o;
    }

    $o->outcome('pass');

    return $o;
}

__PACKAGE__->meta->make_immutable;
1;
