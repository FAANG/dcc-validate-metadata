
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

package Bio::Metadata::Loader::XMLExperimentLoader;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use Bio::Metadata::Entity;

with "Bio::Metadata::Loader::XMLLoaderRole";

sub hash_to_object {
  my ( $self, $hash ) = @_;

  my $o = Bio::Metadata::Entity->new();

  #get id from XML
  my $id=$hash->{'EXPERIMENT'}->{'accession'};
  $o->id($id);

  #get type from XML
  my $type=(keys %{$hash})[0];
  $o->entity_type($type);

  #set 'links' in Entity.pm
  my $study_id=$hash->{'EXPERIMENT'}->{'STUDY_REF'}->{'accession'};
  my $study = Bio::Metadata::Entity->new(
					 id          => $study_id,
					 entity_type => 'study');

  my $sample_id=$hash->{'EXPERIMENT'}->{'DESIGN'}->{'SAMPLE_DESCRIPTOR'}->{'accession'};
  my $sample = Bio::Metadata::Entity->new(
					  id          => $sample_id,
					  entity_type => 'sample');

  $o->add_link($study);
  $o->add_link($sample);

  #set 'attributes' in Entity.pm
  #arrayref of hashes
  my $attrb_array=$hash->{'EXPERIMENT'}->{'EXPERIMENT_ATTRIBUTES'}->{'EXPERIMENT_ATTRIBUTE'};

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
  
  foreach my $experiment (@$array) {

    my $o = Bio::Metadata::Entity->new();
    #get id from XML
    my $id=$experiment->{'accession'};
    $o->id($id);

    #set type
    $o->entity_type($type);

     #set 'links' in Entity.pm
    my $study_id=$experiment->{'STUDY_REF'}->{'accession'};
    my $study = Bio::Metadata::Entity->new(
					   id          => $study_id,
					   entity_type => 'study');

    my $sample_id=$experiment->{'DESIGN'}->{'SAMPLE_DESCRIPTOR'}->{'accession'};
    my $sample = Bio::Metadata::Entity->new(
					    id          => $sample_id,
					    entity_type => 'sample');

    $o->add_link($study);
    $o->add_link($sample);

    my $attrb_array=$experiment->{'EXPERIMENT_ATTRIBUTES'}->{'EXPERIMENT_ATTRIBUTE'};
    
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
  print "hello\n";
  
}

__PACKAGE__->meta->make_immutable;
1;
