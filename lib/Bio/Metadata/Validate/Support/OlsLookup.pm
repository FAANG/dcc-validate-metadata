
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

package Bio::Metadata::Validate::Support::OlsLookup;

use Moose;
use REST::Client;
use URI::Escape::XS qw/uri_escape/;
use JSON;
use Try::Tiny;
use Memoize;
use Carp;
use List::Util qw(none);

#cache all calls to the rest service
memoize('is_descendent');

has 'base_url' => (
    is       => 'rw',
    isa      => 'Str',
    required => 1,
    default  => 'http://www.ebi.ac.uk/ols/beta/api'
);
has 'rest_client' => (
    is       => 'rw',
    isa      => 'REST::Client',
    required => 1,
    default  => sub { REST::Client->new() }
);

sub is_descendent {
    my ( $self, $uri, $qfields, $ancestor_uri, $exact ) = @_;

    if ( !ref $qfields ) {
        $qfields = [$qfields];
    }

    my @uri_elements = (
        $self->base_url,
        '/search?q=',
        uri_escape($uri),
        '&exact=',
        $exact,
        '&fieldList=label&groupField=true&childrenOf=',
        uri_escape($ancestor_uri)
    );
    my @valid_qfields =
      qw(label synonym description short_form obo_id annotations logical_description iri);

    for my $qf (@$qfields) {
        if ( none { $_ eq $qf } @valid_qfields ) {
            croak(
                " Invalid query field. Got $qf but should be one of "
                  . join(', '),
                @valid_qfields
            );
        }

        push @uri_elements, '&queryFields=', uri_escape($qf);
    }

    my $request_uri = join( '', @uri_elements );

    my $response = $self->rest_client->GET($request_uri);

    if ( $response->responseCode != 200 ) {
        croak(  'Unsuccessful search - got status code '
              . $response->responseCode . ' for '
              . $request_uri );
    }
    my $response_content = $response->responseContent;

    my $search_result;

    try {
        $search_result = decode_json($response_content);
    }
    catch {
        croak
          "Could not convert response content to JSON from $request_uri: $_";
    };

    my $num_found = $search_result->{response}->{numFound};

    if ( !defined $num_found ) {
        croak "Could not find numFound in search result for $request_uri";
    }

    if ( $num_found > 1 || $num_found < 0 ) {
        croak "Num found was $num_found, but we expect 1 or 0 for $request_uri";
    }

    if ( $num_found == 0 ) {
        return undef;
    }

    my $label = $search_result->{response}{docs}[0]{label};

    if ( !defined $label ) {
        croak "Could not find label in search result for $request_uri";
    }

    return $label;
}

1;
