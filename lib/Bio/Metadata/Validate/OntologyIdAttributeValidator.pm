
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

package Bio::Metadata::Validate::OntologyIdAttributeValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use Try::Tiny;

use URI;
use Text::Unidecode;
use Bio::Metadata::Validate::Support::OlsLookup;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'ols_lookup' => (
    is      => 'rw',
    isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
    default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !$attribute->value || !$attribute->id ) {
        $o->outcome('error');
        $o->message('value and ID required');
        return $o;
    }

    my $matching_term;
  ANCESTOR: for my $valid_term ( $rule->all_valid_terms ) {
        $matching_term =
          $self->ols_lookup->find_matchnotall( $attribute->id, $valid_term, undef );
        if ($matching_term) {
            last ANCESTOR;
        }
    }

    if ( !$matching_term ) {
        $o->outcome('error');
        $o->message('term is not a descendent of a valid ancestor');
        return $o;
    }


    my $label = $matching_term->{label};

    #unicode support is variable, use Unidecode to normalise for this
    my ($normalised_label,$normalised_value) = map {unidecode($_)} ($label, $attribute->value);

    if ( $normalised_label ne $normalised_value ) {
        $o->outcome('warning');
        $o->message(
            "value ($normalised_value) does not precisely match label ($normalised_label) for term ".$attribute->id);
        return $o;
    }

    $o->outcome('pass');

    return $o;
}

__PACKAGE__->meta->make_immutable;
1;
