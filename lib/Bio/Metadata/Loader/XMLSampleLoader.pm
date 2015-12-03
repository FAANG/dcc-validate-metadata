
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

package Bio::Metadata::Loader::XMLSampleLoader;

use strict;
use warnings;

use Carp;
use Moose;
use Data::Dumper;
use namespace::autoclean;
use Bio::Metadata::Entity;

with "Bio::Metadata::Loader::XMLLoaderRole";

sub hash_to_object {
  my ( $self, $hash ) = @_;

  my $o = Bio::Metadata::Entity->new();

  #get id from XML
  my $id=$hash->{'SAMPLE'}->{'alias'};
  $o->id($id);

  #get type from XML
  my $type=(keys %{$hash})[0];
  $o->entity_type($type);

  #set 'attributes' in Entity.pm
  #arrayref of hashes
  my $attrb_array=$hash->{'SAMPLE'}->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'};

  foreach my $attrb (@$attrb_array) {
    my $o_attrb= Bio::Metadata::Attribute->new(
					 name => $attrb->{'TAG'},
					 value => $attrb->{'VALUE'}
					);
    $o->add_attribute($o_attrb);
  }

  return $o;
}

sub array_to_object {
  my ( $self, $array, $type ) = @_;

  my @objects;
  
  foreach my $sample (@$array) {

    my $o = Bio::Metadata::Entity->new();
    #get id from XML
    my $id=$sample->{'alias'};
    $o->id($id);

    #set type
    $o->entity_type($type);

    my $attrb_array=$sample->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'};

    if (ref $attrb_array eq 'HASH') {
      my $o_attrb= Bio::Metadata::Attribute->new(
						 name => $attrb_array->{'TAG'},
						 value => $attrb_array->{'VALUE'}
						);
      $o->add_attribute($o_attrb);
    } elsif (ref $attrb_array eq 'ARRAY') {
      foreach my $attrb (@$attrb_array) {
	$attrb->{'TAG'}="NA" if ref $attrb->{'TAG'};
	$attrb->{'VALUE'}="NA" if ref $attrb->{'VALUE'};
	my $o_attrb= Bio::Metadata::Attribute->new(
						   name => $attrb->{'TAG'},
						   value => $attrb->{'VALUE'}
						  );
	$o->add_attribute($o_attrb);
      }
    }
    push @objects,$o;
  }

  return \@objects;
}

__PACKAGE__->meta->make_immutable;
1;
