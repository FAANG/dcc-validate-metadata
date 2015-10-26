# Copyright 2015 European Molecular Biology Laboratory - European Bioinformatics Institute
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
package Bio::Metadata::XML;

use strict;
use warnings;

use Moose;
use XML::Simple;
use namespace::autoclean;
use Data::Dumper;

extends 'Bio::Metadata::Entity';

#convert a XML file into Perl Hash
sub get_hash_from_file {
  my ($self,$file)=@_;
  
  my $xml = new XML::Simple;
  my $data = $xml->XMLin($file,KeepRoot => 1);

  return $data;
}

#set 'id' in parent class
sub set_id {
  my ($self,$data)=@_;

  my $id=$data->{'EXPERIMENT'}->{'accession'};

  $self->id($id);
}

#set 'entity_type' in parent class
sub set_type {
  my ($self,$data)=@_;

  my $type=(keys %{$data})[0];

  $self->entity_type($type);
}

#set 'links' in parent class
sub set_links {
   my ($self,$data)=@_;
   
   #study
   my $study_id=$data->{'EXPERIMENT'}->{'STUDY_REF'}->{'accession'};
   my $study = Bio::Metadata::Entity->new(
					  id          => $study_id,
					  entity_type => 'study');

   my $sample_id=$data->{'EXPERIMENT'}->{'DESIGN'}->{'SAMPLE_DESCRIPTOR'}->{'accession'};
   my $sample = Bio::Metadata::Entity->new(
					  id          => $sample_id,
					  entity_type => 'study');


   $self->add_link($study);
   $self->add_link($sample);   
}

#set 'attributes in parent class
sub set_attributes {
  my ($self,$data)=@_;

  #arrayref of hashes
  my $attrb_array=$data->{'EXPERIMENT'}->{'EXPERIMENT_ATTRIBUTES'}->{'EXPERIMENT_ATTRIBUTE'};

  foreach my $attrb (@$attrb_array) {
    my $o= Bio::Metadata::Attribute->new(
					 name => $attrb->{'TAG'},
					 value => $attrb->{'VALUE'}
					);
    $self->add_attribute($o);
  }
  print "h\n";
}

1;
