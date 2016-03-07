
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
use Carp;
use List::Util qw(none);
use Cache::LRU;

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
has 'cache' => (
  is       => 'rw',
  isa      => 'Cache::LRU',
  required => 1,
  default  => sub { Cache::LRU->new( size => 10000 ) }
);
has 'valid_qfields' => (
  is      => 'ro',
  traits  => ['Array'],
  isa     => 'ArrayRef[Str]',
  default => sub {
    [
      qw(label synonym description short_form obo_id annotations logical_description iri)
    ];
  },
  handles => { find_valid_qfield => 'first', join_valid_qfields => 'join' },

);

sub _cache_key {
  my ( $self, @fields ) = @_;
  return join( '#', @fields );
}

sub is_descendent {
  my ( $self, $query, $qfields, $ancestor_uri, $exact ) = @_;

  if ( !ref $qfields ) {
    $qfields = [$qfields];
  }
  my $cache_key = $self->_cache_key( $query, @$qfields, $ancestor_uri, $exact );
  my $cached_entry = $self->cache->get($cache_key);

  if ( defined $cached_entry ) {
    return $cached_entry;
  }
  my $label = $self->_is_descendent( $query, $qfields, $ancestor_uri, $exact );

  if ( !$label ) {
    $label = $self->_is_same( $query, $ancestor_uri );
  }

  $self->cache->set( $cache_key => $label );

  return $label;
}

sub _is_same {
  my ( $self, $query, $ancestor_uri,  ) = @_;

  my $fields = [qw(short_form obo_id label)];
  my $exact = 'true';

  my @uri_elements = (
    $self->base_url,
    '/search?q=',
    uri_escape($ancestor_uri),
    '&qfield=iri&exact=',
    $exact,
    '&groupField=true',
    map { '&fieldList=' . uri_escape($_) } ( @$fields ),
  );
  my $request_uri = join( '', @uri_elements );

  my $search_result = $self->request_to_json( join( '', @uri_elements ) );

  my $num_found = $search_result->{response}->{numFound};
  if ( !defined $num_found ) {
    croak "Could not find numFound in search result for $request_uri";
  }

  if ( $num_found > 1 || $num_found < 0 ) {
    croak "Num found was $num_found, but we expect 1 or 0 for $request_uri";
  }

  if ( $num_found == 0 ) {
    return '';
  }
  my $term = $search_result->{response}{docs}[0];

  if ($term->{obo_id} eq $query || $term->{short_form} eq $query){
    return $term->{label}
  }
  return '';
}

sub _is_descendent {
  my ( $self, $query, $qfields, $ancestor_uri, $exact ) = @_;

  $self->check_qfields($qfields);

  my @uri_elements = (
    $self->base_url,
    '/search?q=',
    uri_escape($query),
    '&exact=',
    $exact,
    '&fieldList=label&groupField=true&childrenOf=',
    uri_escape($ancestor_uri),
    map { '&queryFields=' . uri_escape($_) } @$qfields
  );
  my $request_uri = join( '', @uri_elements );
  my $search_result = $self->request_to_json($request_uri);
  
  my $num_found = $search_result->{response}->{numFound};

  if ( !defined $num_found ) {
    croak "Could not find numFound in search result for $request_uri";
  }

  if ( $num_found > 1 || $num_found < 0 ) {
    croak "Num found was $num_found, but we expect 1 or 0 for $request_uri";
  }

  if ( $num_found == 0 ) {
    return '';
  }

  my $label = $search_result->{response}{docs}[0]{label};

  if ( !defined $label ) {
    croak "Could not find label in search result for $request_uri";
  }

  return $label;
}

sub check_qfields {
  my ( $self, $qfields ) = @_;

  for my $qf (@$qfields) {
    if ( !$self->find_valid_qfield( sub { $_ eq $qf } ) ) {
      croak( " Invalid query field. Got $qf but should be one of "
          . $self->join_valid_qfields(',') );
    }
  }
}

sub request_to_json {
  my ( $self, $request_uri ) = @_;

  my $response = $self->rest_client->GET($request_uri);

  if ( $response->responseCode != 200 ) {
    croak('Unsuccessful search - got status code '
        . $response->responseCode . ' for '
        . $request_uri );
  }

  my $result;

  try {
    $result = decode_json( $response->responseContent );
  }
  catch {
    croak "Could not convert response content to JSON from $request_uri: $_";
  };

  return $result;
}

1;
