
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
use Bio::Metadata::Loader::JSONAttrLinkLoader;

with "Bio::Metadata::Loader::XMLLoaderRole";

has 'attr_links'  => ( is => 'rw', isa => 'Str' );

sub hash_to_object {
  my ( $self, $hash, $type ) = @_;

  my $o = Bio::Metadata::Entity->new();
  
  my $id=$hash->{'alias'};
  $o->id($id);
  $o->entity_type($type);

  #set 'attributes' in Entity.pm
  #arrayref of hashes
  my $attrb_array;
  
  if (ref $hash->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'} eq 'ARRAY') {
	  $attrb_array=$hash->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'};
  } elsif(ref $hash->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'} eq 'HASH') {
  	  push @$attrb_array,$hash->{'SAMPLE_ATTRIBUTES'}->{'SAMPLE_ATTRIBUTE'};
  }

  foreach my $attrb (@$attrb_array) {
	  my $tag=$attrb->{'TAG'};
	  my $value=$attrb->{'VALUE'};
	  $tag="NA" if ref $tag;
	  $value="NA" if ref $value;
	  
	  my $o_attrb= Bio::Metadata::Attribute->new(
	  	name => $tag,
		value => $value
		);
		$o->add_attribute($o_attrb);
  }
  
  if ($self->attr_links) {
	  my $attr_links = Bio::Metadata::Loader::JSONAttrLinkLoader->new()->load($self->attr_links);
  
  	my $attrs=$o->organised_attr;
  	foreach my $link (@$attr_links) {
		next if !exists $attrs->{$link->attr1}->[0] || !exists $attrs->{$link->attr2}->[0];
	  	my $attr1=$attrs->{$link->attr1}->[0];
	  	my $attr2=$attrs->{$link->attr2}->[0];
	  	my $prop2=$link->prop2;
		$attr1->$prop2($attr2->value);
  	}
  }
  return $o;
}

__PACKAGE__->meta->make_immutable;
1;
