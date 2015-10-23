
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
use REST::Client;
use URI::Escape::XS qw/uri_escape/;
use JSON;
use Memoize;

#cache all calls to the rest service
memoize('is_descendent');

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'base_url' => (is => 'rw', isa => 'Str', required => 1, default => 'http://www.ebi.ac.uk/ols/beta/api');
has 'rest_client' => (is => 'rw', isa => 'REST::Client', required => 1, default => sub { REST::Client->new()});

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !$attribute->value || !$attribute->uri ) {
        $o->outcome('error');
        $o->message('value and uri required');
        return $o;
    }

    my $uri;
    try {
      $uri = URI->new($attribute->uri);
    }
    catch {
      $o->outcome('error');
      $o->message('uri is not valid');
      return $o;
    };
    
    my $label;
    ANCESTOR: for my $ancestor_uri ($rule->all_valid_ancestor_uris) {
      $label = $self->is_descendent($attribute->uri,$ancestor_uri);
      if ($label){
        last ANCESTOR;
      }
    }
    
    if (!$label){
      $o->outcome('error');
      $o->message('uri is not descendent of valid ancestor');
      return $o;
    }
    
    if ($label ne $attribute->value){
      $o->outcome('warning');
      $o->message('value does not precisely match ontology term label - '.$label);
      return $o;
    }
    
    $o->outcome('pass'); 
    
    return $o;
}

sub is_descendent {
  my ($self,$uri,$ancestor_uri) = @_;
  
  my $request_uri = $self->base_url.'/search?q=' .uri_escape($uri).'&exact=true&fieldList=label&groupField=true&childrenOf='.uri_escape($ancestor_uri);
  my $response = $self->rest_client->GET($request_uri);
  
  if ($response->responseCode != 200){
    croak('Unsuccessful search - got status code '.$response->responseCode.' for '.$request_uri );
  }
  my $response_content = $response->responseContent;
   
  my $search_result; 
   
  try {
      $search_result = decode_json($response_content);
  }
  catch {
      croak "Could not convert response content to JSON from $request_uri: $_";
  };
  
  my $num_found = $search_result->{response}->{numFound};
  
  if (!defined $num_found){
    croak "Could not find numFound in search result for $request_uri";
  }
  
  if ($num_found > 1 || $num_found < 0){
    croak "Num found was $num_found, but we expect 1 or 0 for $request_uri";
  }
  
  if ($num_found == 0){
    return undef;
  }
  
  my $label = $search_result->{response}{docs}[0]{label};
  
  if (!defined $label){
        croak "Could not find label in search result for $request_uri";
  }
  
  return $label;
}



__PACKAGE__->meta->make_immutable;
1;
