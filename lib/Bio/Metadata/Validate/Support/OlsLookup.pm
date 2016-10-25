
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
use JSON::MaybeXS;
use Try::Tiny;
use Carp;
use List::Util qw(none any);
use Cache::LRU;

has 'base_url' => (
  is       => 'rw',
  isa      => 'Str',
  required => 1,
  default  => 'http://www.ebi.ac.uk/ols/api'
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
  default  => sub { Cache::LRU->new( size => 200 ) }
);
has 'qfields' => (
  is      => 'ro',
  traits  => ['Array'],
  isa     => 'ArrayRef[Str]',
  default => sub {
    [qw(label short_form obo_id iri)];
  },
  handles => {
    all_qfields        => 'elements',
    find_valid_qfield  => 'first',
    join_valid_qfields => 'join'
  },
);
has 'request_size' => (
  is      => 'ro',
  isa     => 'Int',
  default => 1000
);

sub _cache_key {
  my ( $self, @fields ) = @_;
  return join( '#', @fields );
}

sub find_match {
  my ( $self, $query, $permitted_term, $exact ) = @_;

  my $pth = $permitted_term->to_hash;
  my $cache_key =
    $self->_cache_key( $query, $exact // 0,
    map { $pth->{$_} } sort keys %$pth );

  my $cache_value = $self->cache->get($cache_key);

  if ( defined $cache_value ) {
    return $cache_value;
  }
  else {
    my $value = $self->_find_match( $query, $permitted_term, $exact );

    #OLS loading of ATOL and EOL terms is currently giving IDs like owlATOL_00001
    if ( !$value
      && ($permitted_term->ontology_name eq 'ATOL' || $permitted_term->ontology_name eq 'EOL' )
      && begins_with( $query, $permitted_term->ontology_name )
    )
    {
      $value = $self->_find_match( 'owl' . $query, $permitted_term, $exact );
    }

    $self->cache->set( $cache_key, $value );
    return $value;
  }
}

sub find_match_all_children {
  my ( $self, $query, $permitted_term, $exact ) = @_;

  my $pth = $permitted_term->to_hash;
  my $cache_key =
    $self->_cache_key( $query, $exact // 0,
    map { $pth->{$_} } sort keys %$pth );

  my $cache_value = $self->cache->get($cache_key);

  if ( defined $cache_value ) {
    return $cache_value;
  }
  else {
    my $value = $self->_find_match_all_children( $query, $permitted_term, $exact );

    #OLS loading of ATOL and EOL terms is currently giving IDs like owlATOL_00001
    if ( !$value
      && ($permitted_term->ontology_name eq 'ATOL' || $permitted_term->ontology_name eq 'EOL' )
      && begins_with( $query, $permitted_term->ontology_name )
    )
    {
      $value = $self->_find_match_all_children( 'owl' . $query, $permitted_term, $exact );
    }

    $self->cache->set( $cache_key, $value );
    return $value;
  }
}

sub begins_with {
  return substr( $_[0], 0, length( $_[1] ) ) eq $_[1];
}

sub _find_match {
  my ( $self, $query, $permitted_term, $exact ) = @_;

  my @uri_elements = (
    $self->base_url,
    '/search?q=',
    uri_escape($query),
    '&exact=',
    $exact ? 'true' : 'false',
    '&groupField=true',
    '&childrenOf=',
    uri_escape( $permitted_term->term_iri ),
    '&ontology=',
    lc( $permitted_term->ontology_name ),
    map { '&queryFields=' . uri_escape($_) } $self->all_qfields,
  );
  my $request_uri = join( '', @uri_elements );
  my $search_result = $self->request_to_json($request_uri);

  if ( $search_result->{response}{docs} && $search_result->{response}{docs}[0] )
  {
    return $search_result->{response}{docs}[0];
  }

  if ( $permitted_term->include_root ) {
    my $terms = $self->_matching_terms( $permitted_term->ontology_name,
      $permitted_term->term_iri, 0, 0, 1 );

    if ( $terms->[0] && grep { $query eq $terms->[0]{$_} } $self->all_qfields )
    {
      return $terms->[0];
    }
  }

  return '';
}

sub _find_match_all_children {
  my ( $self, $query, $permitted_term, $exact ) = @_;

  my @uri_elements = (
    $self->base_url,
    '/search?q=',
    uri_escape($query),
    '&exact=',
    $exact ? 'true' : 'false',
    '&groupField=true',
    '&allchildrenOf=',
    uri_escape( $permitted_term->term_iri ),
    '&ontology=',
    lc( $permitted_term->ontology_name ),
    map { '&queryFields=' . uri_escape($_) } $self->all_qfields,
  );
  my $request_uri = join( '', @uri_elements );
  my $search_result = $self->request_to_json($request_uri);

  if ( $search_result->{response}{docs} && $search_result->{response}{docs}[0] )
  {
    return $search_result->{response}{docs}[0];
  }

  if ( $permitted_term->include_root ) {
    my $terms = $self->_matching_terms( $permitted_term->ontology_name,
      $permitted_term->term_iri, 0, 0, 1 );

    if ( $terms->[0] && grep { $query eq $terms->[0]{$_} } $self->all_qfields )
    {
      return $terms->[0];
    }
  }

  return '';
}

sub matching_terms {
  my ( $self, $permitted_term ) = @_;

  my @args = (
    $permitted_term->ontology_name,     $permitted_term->term_iri,
    $permitted_term->allow_descendants, $permitted_term->leaf_only,
    $permitted_term->include_root
  );

  my $cache_key = $self->_cache_key(@args);

  my $cached_value = $self->cache->get($cache_key);
  if ( defined $cached_value ) {
    return $cached_value;
  }
  else {
    my $matching_terms = $self->_matching_terms(@args);
    my $reduced_terms  = $self->_reduce_terms($matching_terms);
    my $uniq_terms     = $self->_uniq_terms($reduced_terms);
    $self->cache->set( $cache_key, $uniq_terms );
    return $uniq_terms;
  }
}

sub _reduce_terms {
  my ( $self, $terms_json ) = @_;
  my @terms = map {
    {
      label      => $_->{label},
      short_form => $_->{short_form},
      obo_id     => $_->{obo_id},
      iri        => $_->{iri}
    }
  } @$terms_json;

  return \@terms;
}

sub _matching_terms {
  my (
    $self,              $ontology_name, $term_iri,
    $allow_descendants, $leaf_only,     $include_root
  ) = @_;

  my @uri_elements = (
    $self->base_url, '/ontologies/', uri_escape( lc($ontology_name) ),
    '/terms/', uri_escape( uri_escape($term_iri) )
  );
  my $term_uri = join( '', @uri_elements );
  my $root_term_json = $self->request_to_json($term_uri);

  my @terms_json;

  push @terms_json, $root_term_json if ($include_root);

  if ($allow_descendants) {
    my $next_uri =
        $root_term_json->{_links}{descendants}
      ? $root_term_json->{_links}{descendants}{href}
      . '?size='
      . $self->request_size
      : undef;

    while ($next_uri) {
      my $json = $self->request_to_json($next_uri);

      $next_uri =
        exists $json->{_links}{next} ? $json->{_links}{next}{href} : undef;

      if ( $json->{_embedded}{terms} ) {
        my $terms_in_page = $json->{_embedded}{terms};
        push @terms_json, @$terms_in_page;
      }
    }
  }

  if ($leaf_only) {
    @terms_json = grep { !$_->{has_children} } @terms_json;
  }
  return \@terms_json;
}

sub _uniq_terms {
  my ( $self, $terms ) = @_;

  my %h;
  my @u;
  for my $t (@$terms) {
    if ( !$h{ $t->{iri} }++ ) {
      push @u, $t;
    }
  }

  return \@u;
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

__PACKAGE__->meta->make_immutable;
1;
