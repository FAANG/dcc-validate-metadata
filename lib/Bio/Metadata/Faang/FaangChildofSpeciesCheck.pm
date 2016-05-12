
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

use Bio::Metadata::Validate::Support::BioSDLookup;
use Bio::Metadata::Rules::PermittedTerm;

has description => (
  is  => 'rw',
  isa => 'Str',
  default =>
    'Ensure that the child of species is consistent with their parents reported species.',
);

has name => (
  is      => 'rw',
  isa     => 'Str',
  default => 'Childofspecies/Parentsspecies',
);

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'entities_by_id' => (
    traits  => ['Hash'],
    is      => 'rw',
    isa     => 'HashRef[Bio::Metadata::Entity]',
    handles => { get_entity_by_id => 'get' },
);

has 'biosd_lookup' => (
    is  => 'rw',
    isa => 'Bio::Metadata::Validate::Support::BioSDLookup',
    required => 1,
    default => sub {Bio::Metadata::Validate::Support::BioSDLookup->new()},
);

sub check_entity {
  my ( $self, $entity, $entities_by_id ) = @_;
  my @outcomes;

  my $organised_attr = $entity->organised_attr;
  my $child_species_attrs  = $organised_attr->{'organism'};
  my $parents_ids = $organised_attr->{'Child Of'};

  unless ( $child_species_attrs
    && scalar(@$child_species_attrs) == 1
    && $child_species_attrs->[0]->id
    && $parents_ids
    && scalar(@$parents_ids) > 0 )
  {
    #not enough information for higher level checks
    return \@outcomes;
  }
  
  my @all_species = ($child_species_attrs{value});
  
  foreach my $sample_identifier (@{$parents_ids}){
    my $entity = $self->get_entity_by_id($sample_identifier);
    if ( !defined $entity) {
      $entity = $self->biosd_lookup->fetch_sample($sample_identifier);
    }

    if ( !defined $entity ) {
        $o->outcome('error');
        $o->message('No entity found');
        return $o;
    }
    my $organised_attr = $entity->organised_attr;

    my $child_species_attrs  = $organised_attr->{'organism'};
    my $species_attrs  = $organised_attr->{'organism'};
    push(@all_species, $child_species_attrs{value})
  }

  my @mismatched_species;
  my %test_if_equal = map { $_, 1 } @test;
  if (!keys %string == 1) {
    @mismatched_species = values(%test_if_equal);
  }

  my $outcome =
    Bio::Metadata::Validate::ValidationOutcome->new( attributes => $breed_attrs,
    );
  push @outcomes, $outcome;

  if (@mismatched_species) {
    $outcome->outcome('error');
    $outcome->message(
      "The species of the organism does not match the species of the parents listed in 'Child Of': "
        . join( ', ', @mismatched_breeds ) );
  }
  else {
    $outcome->outcome('pass');
  }

  return \@outcomes;
}

__PACKAGE__->meta->make_immutable;

1;
