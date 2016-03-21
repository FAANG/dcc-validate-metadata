
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

	 my $org_attrbs=$entity->organised_attr(1);

	 if ($self->selector) {
		 die("[ERROR] attribute ",$self->selector," is not a valid 'selector' attribute") if !exists($org_attrbs->{$self->selector});
	 }

     my $validator = JSON::Validator->new;
     $validator->schema($self->schema());

	 my $hash=$entity->to_hash();

	 my $attrbs=$self->prepare_attrs($entity);

	 $hash->{'attributes'}=();
	 $hash->{'attributes'}->{'SELECTOR'}=$attrbs;

	 my @warnings = $validator->validate($hash);

	 my @outcomes;
	 my $outcome_overall='pass';

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

	my $not_branch;
	my $selector=$self->selector;

	my @a=split/\[\d+\]/,$w->message;

	if ($self->selector) {
		foreach my $a (@a) {
			$a=~s/^\s\///;
			if ($a=~/$selector\: Not in enum list\:/) {
				$not_branch=$1 if $a=~/branch\:(\d+)\]/;
				last;
			}
		}
	}

	$not_branch="n.a." if !$not_branch;

	my @warnings;

	foreach my $a (@a) {
		next if $a=~/branch\:$not_branch\]/;
		next if $a=~/oneOf failed\:\s\(/;
		my $msg;
		$a=~s/^\s\///;
		$a=~s/\[\w+\sbranch\:\d+\][\s|\)]//;
		my $name=$1 if $a=~/^(\w+)\:\s.+/;
		die("[ERROR] Attribute was not found") if !$name;
		$msg.="[ATTRIBUTE]:".$a;
		push @warnings,&E($name,$msg);
	}

	return \@warnings;

}

sub E { bless {path => $_[0] || '/', message => $_[1]}, 'JSON::Validator::Error'; }

1;
