
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

package Bio::Metadata::Faang::FaangChildOfSpeciesCheck;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use List::MoreUtils qw(uniq);

use Bio::Metadata::Validate::Support::BioSDLookup;
use Bio::Metadata::Rules::PermittedTerm;

has description => (
  is  => 'rw',
  isa => 'Str',
  default =>
    'Ensure that the child species is consistent with their parents reported species listed in child of.',
);

has name => (
  is      => 'rw',
  isa     => 'Str',
  default => 'Childspecies/Parentsspecies',
);

#must consume after declaring attribute that satisfies requirement for 'description'
with 'Bio::Metadata::Consistency::ConsistencyCheckRole';

has 'biosd_lookup' => (
    is  => 'rw',
    isa => 'Bio::Metadata::Validate::Support::BioSDLookup',
    required => 1,
    default => sub {Bio::Metadata::Validate::Support::BioSDLookup->new()},
);

sub check_entity {
  my ( $self, $entity, $entities_by_id ) = @_;
  my @outcomes;
  
  my @all_species;
  my $organised_attr = $entity->organised_attr;
  my $child_species_attrs  = $organised_attr->{'organism'};
  my $parents_ids = $organised_attr->{'child of'};

  unless ( $child_species_attrs
    && scalar(@$child_species_attrs) == 1
    && $child_species_attrs->[0]->id
    && $parents_ids
    && scalar(@$parents_ids) > 0 )
  {
    #not enough information for higher level checks
    return \@outcomes;
  }

  my $child_species = $child_species_attrs->[0]->{'value'};
  push(@all_species, $child_species);
  my @parent_species;

  foreach my $sample_identifier (@{$parents_ids}){
    my $parent_entity;
    if ($entities_by_id->{$sample_identifier->{'value'}}){
      $parent_entity = $entities_by_id->{$sample_identifier->{'value'}};
    }
    if ( !defined $parent_entity) {
      $parent_entity = $self->biosd_lookup->fetch_sample($sample_identifier->{'value'});
    }

    my $parent_organised_attr = $parent_entity->organised_attr;
    my $parent_species_attrs  = $parent_organised_attr->{'organism'};
    
    push(@parent_species, $parent_species_attrs->[0]->{'value'});
    push(@all_species, $parent_species_attrs->[0]->{'value'});
  }

  #Get unique species, should be one if parents and child match
  my @test_if_equal = uniq @all_species;

  my $outcome =
    Bio::Metadata::Validate::ValidationOutcome->new( attributes => $child_species_attrs,
    );
  push @outcomes, $outcome;

  #Test if more than one species i.e. child and parent mismatch
  if (scalar(@test_if_equal) > 1) {
    $outcome->outcome('error');
    $outcome->message(
      "The species of the child ($child_species) does not match the species of the parents: "
        . join( ', ', @parent_species ) );
    print "Made it error\n";
  }
  else {
    print "Made it pass\n";
    $outcome->outcome('pass');
  }

  return \@outcomes;
}

__PACKAGE__->meta->make_immutable;

1;
