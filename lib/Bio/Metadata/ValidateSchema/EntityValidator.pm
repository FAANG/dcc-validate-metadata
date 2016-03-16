
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
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;

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

has 'selector' => (
	is => 'rw',
	isa => 'Str',
	required => 0
);

sub validate {
	 my ($self,$entity)=@_;
	 
	 my $org_attrbs=$entity->organised_attr;
  
     my $validator = JSON::Validator->new;
     $validator->schema($self->schema());
	 
	 my $hash=$entity->to_hash();
	 
	 my $attrbs=$self->prepare_attrs($entity);
	 
	 $hash->{'attributes'}=();
	 $hash->{'attributes'}->{'SELECTOR'}=$attrbs;
	 	 
	 my @outcomes;
	 my $outcome_overall='pass';
	 
	 if ($self->selector) {
		 warn("[ERROR] attribute ",$self->selector," is not a valid 'selector' attribute for entity with alias:",$entity->id,
		 ".\n\tMaybe this attribute is not present in this Entity?.\n\tSkipping...\n") if !exists($org_attrbs->{$self->selector});
		 if (!exists($org_attrbs->{$self->selector})) {
			my $msg="attribute ".$self->selector." selector is not present";
		 	my $v_outcome= Bio::Metadata::Validate::ValidationOutcome->new;
			$v_outcome->entity($entity);
			$v_outcome->message($msg);
	  		$v_outcome->outcome('error');
			my $rule= Bio::Metadata::Rules::Rule->new (
				mandatory=> 'mandatory',
				name=> $self->selector,
				type=> 'text'
			);
			$v_outcome->rule($rule);
			push @outcomes,$v_outcome;
			return ('error',\@outcomes);
		 }
	 }

	 my @warnings = $validator->validate($hash);
	 
	 if (@warnings) {
		 my $new_warnings=$self->prepare_warnings($warnings[0]);

         foreach my $w (@$new_warnings) {
			$outcome_overall='warning' unless $outcome_overall eq 'error' ;
			my $v_outcome= Bio::Metadata::Validate::ValidationOutcome->new;
			$v_outcome->entity($entity);
			$v_outcome->outcome('warning');
		 	my $attr_name = $w->path;
			$v_outcome->message($w->message);
			if (exists($org_attrbs->{$attr_name})) {
				my $failed_attr=$org_attrbs->{$attr_name};
				$v_outcome->attributes($failed_attr);
		  	} else {
		  		$v_outcome->outcome('error');
				my $rule= Bio::Metadata::Rules::Rule->new (
					mandatory=> 'mandatory',
					name=> $attr_name,
					type=> 'text'
				);
				$v_outcome->rule($rule);
				$outcome_overall='error';
		  	}
			push @outcomes,$v_outcome;			 
		 }
	 } else {
		my $v_outcome= Bio::Metadata::Validate::ValidationOutcome->new;
		$v_outcome->entity($entity);
		$v_outcome->outcome('pass');
		my $rule= Bio::Metadata::Rules::Rule->new (
			mandatory=> 'mandatory',
			name=> 'schema',
			type=> 'text'
		);
		$v_outcome->rule($rule);
		$v_outcome->message('pass');
		push @outcomes,$v_outcome;	 
	 }
	 
	 return ($outcome_overall,\@outcomes);
}

sub validate_all {
	my ($self,$entities)=@_;
	
    my %entity_status;
    my %entity_outcomes;
    my %attribute_status;
    my %attribute_outcomes;
  
  
    for my $e (@$entities){
	
	  warn("[INFO] Validating sample ",$e->id,"\n");

      my ($status, $outcomes) = $self->validate($e);
  	
      $entity_status{$e} = $status;
      $entity_outcomes{$e} = $outcomes;
    
      for my $o (@$outcomes) {
        for my $a ($o->all_attributes) {
          if (! exists $attribute_outcomes{$a}){
            $attribute_status{$a} = $o->outcome;
            $attribute_outcomes{$a} = [];
          }
          push @{$attribute_outcomes{$a}}, $o;
        
          if ($o->outcome eq 'error' && $attribute_status{$a} ne 'error') {
            $attribute_status{$a} = 'error';
          }
          if ($o->outcome eq 'warning' && $attribute_status{$a} eq 'pass'){
            $attribute_status{$a} = 'warning';
          }
        }
      }
    }
  
    return (\%entity_status, \%entity_outcomes, \%attribute_status, \%attribute_outcomes);
}

sub prepare_attrs {
	my ($self,$entity)=@_;
	
	my $old_attrbs=$entity->attributes;
	
	my %new_attrbs;
	
	foreach my $attr (@$old_attrbs) {
		$new_attrbs{$attr->{'name'}}= $attr->{'value'};				
	}
	
	return \%new_attrbs;
}


sub prepare_warnings {
	my ($self,$w)=@_;
	
	my %notbranch;
	my $selector=$self->selector;
	
	my @a=split/\[\d+\]/,$w->message;
	
	if ($self->selector && $w->path=~/SELECTOR/) {
		foreach my $a (@a) {
			$a=~s/^\s\///;
			if ($a=~/$selector\: Not in enum list\:/) {
				$notbranch{$1}=0 if $a=~/branch\:(\d+)\]/;
			}
		}
	}
	
	my @warnings;
	my $seen=0;

	if ($w->path=~/SELECTOR/) {
		foreach my $msg (@a) {
			next if $msg=~/oneOf failed\:\s\(/;
			my $branch=$1 if $msg=~/branch\:(\d+)\]/;
			next if exists($notbranch{$branch});
			$seen=1;
			$msg=~s/^\s\///;
			$msg=~s/\[\w+\sbranch\:\d+\][\s|\)]//;
			my $name=$1 if $msg=~/^(\w+)\:\s.+/;
			die("[ERROR] Attribute was not found") if !$name;
			push @warnings,&E($name,$msg);
		}
    } else {
		my $name=$1 if $w->path=~/\/(\w+)/;
		push @warnings,&E($name,$w->message);
	}
	
	if ($w->path=~/SELECTOR/ && keys(%notbranch)>1 && $seen==0) {
		push @warnings,&E($self->selector,"[ATTRIBUTE]: is not a valid term");
	}
	
	return \@warnings;
	
}

sub E { bless {path => $_[0] || '/', message => $_[1]}, 'JSON::Validator::Error'; }

1;
