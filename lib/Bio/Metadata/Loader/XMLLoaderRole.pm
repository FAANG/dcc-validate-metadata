
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

package Bio::Metadata::Loader::XMLLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;

use XML::Simple;
use Try::Tiny;
use autodie;
use Data::Dumper;
use MooseX::Params::Validate;
use Bio::Metadata::Types;

requires 'hash_to_object';

sub load {
  my ( $self, $file_path ) = @_;
  my ( $xml_data, $o );
  try {
    my $xml = new XML::Simple;
    $xml_data = $xml->XMLin($file_path,KeepRoot => 1);
  }
  catch {
    croak "Failed to read from $file_path: $_";
  };

	my $entity_type;
  try {
    my @root = keys(%$xml_data);
    if ( $root[0] eq 'ROOT' ) {
      
      @root = keys(%{ $xml_data->{ROOT} });
      $entity_type=$root[1];
      print Dumper($entity_type);
		  $o = $self->hash_to_object($$xml_data{ROOT}{$entity_type},$entity_type);
    }
    elsif ( $root[0] =~ /(.*)_SET/ ) {
      $entity_type=$1;
		  my $entities=$xml_data->{$root[0]}->{$entity_type};
      print Dumper(@$entities);
		  $o = [ map { $self->hash_to_object($_, $entity_type) } @$entities ];
    }
  } catch {
    croak "Could not convert data structure to object: $_";
  };
  my @entities;
  push(@entities, $o);
  print "[WARNING] No entities retrieved from $file_path" if !@entities;
  return \@entities;
}

1;
