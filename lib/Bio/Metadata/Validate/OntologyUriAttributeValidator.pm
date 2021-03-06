
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

package Bio::Metadata::Validate::OntologyUriAttributeValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use Try::Tiny;

use URI;
use Bio::Metadata::Validate::Support::OlsLookup;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'ols_lookup' => (
    is      => 'rw',
    isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
    default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !$attribute->value || !$attribute->uri ) {
        $o->outcome('error');
        $o->message('value and uri required');
        return $o;
    }

    my $uri;
    try {
        $uri = URI->new( $attribute->uri );
    }
    catch {
        $o->outcome('error');
        $o->message('uri is not valid');
        return $o;
    };

    if (! $uri->has_recognized_scheme){
      $o->outcome('error');
      $o->message('uri is not valid');
      return $o;
    }

    my $term;
  ANCESTOR: for my $valid_term ( $rule->all_valid_terms ) {
        $term =
          $self->ols_lookup->find_match( $attribute->uri, $valid_term, undef );
        if ($term) {
            last ANCESTOR;
        }
    }

    if ( !$term ) {
        $o->outcome('error');
        $o->message('URI is not for a valid term');
        return $o;
    }

    my $label = $term->{label};
    if ( $label ne $attribute->value ) {
        $o->outcome('warning');
        $o->message(
            'value does not precisely match ontology term label - ' . $label );
        return $o;
    }

    $o->outcome('pass');

    return $o;
}

__PACKAGE__->meta->make_immutable;
1;
