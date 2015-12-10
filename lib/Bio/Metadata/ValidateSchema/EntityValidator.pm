
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

package Bio::Metadata::ValidateSchema::EntityValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use JSON;
use JSON::Validator;

use Data::Dumper;
use Bio::Metadata::Entity;
use MooseX::Params::Validate;

use Bio::Metadata::Attribute;
use Bio::Metadata::ValidateSchema::ValidationOutcome;
use Bio::Metadata::ValidateSchema::ValidationOutcomeSet;

has 'schema' => (
		 is => 'rw',
		 isa => 'Str',
		 required => 1
		);
has 'entity' => (
		 is => 'rw',
		 isa => 'Bio::Metadata::Entity',
		 required => 0
		);
has 'entityarray' => (
		    traits => ['Array'],
		    is => 'rw',
		    isa => 'Bio::Metadata::EntityArrayRef',
		    handles => {
				all_entities   => 'elements',
				add_entities    => 'push',
				count_entities => 'count',
				get_entity    => 'get',
			       },
		    default => sub { [] },
		    coerce => 1,
		    required => 1
		    
		   );

sub validate {
  my ($self)=@_;

  if ($self->count_entities>1) {
    
  } elsif ($self->count_entities==0) {
    $self->add_entities($self->entity);
  }

  my $outcomeset= Bio::Metadata::ValidateSchema::ValidationOutcomeSet->new();
  
  foreach my $entity ($self->all_entities) {

    my $outcome= Bio::Metadata::ValidateSchema::ValidationOutcome->new();
    $outcome->entity($entity);
    $outcome->outcome('pass');
      
    my $hash=$entity->to_hash();

    #prepare attributes for validation
    my @attrbs=@{$hash->{'attributes'}};
    for (my $i=0;$i<scalar(@attrbs);$i++) {
      my $oldhash=$attrbs[$i];
      my %newhash=(
		   $oldhash->{'name'} => $oldhash->{'value'}
		  );
      $attrbs[$i]=\%newhash;
		 
    }

    $hash->{'attributes'}=\@attrbs;
  
    my $validator = JSON::Validator->new;
    $validator->schema($self->schema());

    my @warnings = $validator->validate($hash);

    if (@warnings) {
      
      foreach my $e (@warnings) {
	$outcome->outcome('warning');
	my $w=Bio::Metadata::ValidateSchema::Warning->new();
	$w->path($e->path);
	my $path=$e->path;
	my $number=$1 if $path=~/\/attributes\/(\d+)/;
	my $message;
	if (defined($number)) {
	  my $failed_attr=$outcome->entity->get_attribute($number);
	  $message="ATTRIBUTE-NAME:".$failed_attr->name.";VALUE:".$failed_attr->value."\t".$e->message;
	} else {
	  my $property=$e->path;
	  $property=~s/\///;
	  $message="PROPERTY-NAME:".$property."\t".$e->message;
	}
	$w->message($message);
	$outcome->add_warning($w);
      }
    }
    $outcomeset->add_outcome($outcome);
  }
  return $outcomeset;
}

1;
