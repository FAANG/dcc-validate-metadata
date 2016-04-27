
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

package Bio::Metadata::Faang::FaangBreedSpeciesCheck;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;

use Bio::Metadata::Validate::Support::OlsLookup;
use Bio::Metadata::Faang::FaangBreedParser;
use Bio::Metadata::Rules::PermittedTerm;

has description => (
  is  => 'rw',
  isa => 'Str',
  default =>
    'Ensure that the animal breed is consistent with the species reported.',
);

has name => (
  is      => 'rw',
  isa     => 'Str',
  default => 'Breed/species',
);

#must consume after declaring attribute that satisfies requirement for 'description'
with 'Bio::Metadata::Consistency::ConsistencyCheckRole';

has ols_lookup => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
  default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

has breed_parser => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Faang::FaangBreedParser',
  default => sub { return Bio::Metadata::Faang::FaangBreedParser->new() }
);

has species_permitted_term => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Rules::PermittedTerm',
  default => sub {
    Bio::Metadata::Rules::PermittedTerm->new(
      term_iri      => "http://purl.obolibrary.org/obo/NCBITaxon_1",
      ontology_name => "NCBITaxon"
    );
  },
  coerce => 1
);

has species_to_lbo_breed_mapping => (
  is      => 'rw',
  traits  => ['Hash'],
  isa     => 'HashRef[Str]',
  default => sub {
    {
      'NCBITaxon_89462' => 'LBO_0001042',    #buffalo (Bubalus bubalis)
      'NCBITaxon_9913'  => 'LBO_0000001',    #cattle (Bos taurus)
      'NCBITaxon_9031'  => 'LBO_0000002',    #chicken
      'NCBITaxon_9925'  => 'LBO_0000954',    #goat
      'NCBITaxon_9796'  => 'LBO_0000713',    #horse
      'NCBITaxon_9823'  => 'LBO_0000003',    #pig
      'NCBITaxon_9940'  => 'LBO_0000004',    #sheep
    };
  },
  handles => {
    'get_species_to_lbo_breed_mapping'  => 'get',
    'keys_species_to_lbo_breed_mapping' => 'keys',
  }
);

sub check_entity {
  my ( $self, $entity, $entities_by_id ) = @_;
  my @outcomes;

  my $organised_attr = $entity->organised_attr;
  my $species_attrs  = $organised_attr->{'organism'};
  my $breed_attrs    = $organised_attr->{'breed'};

  unless ( $species_attrs
    && scalar(@$species_attrs) == 1
    && $species_attrs->[0]->id
    && $breed_attrs
    && scalar(@$breed_attrs) == 1 )
  {
    #not enough information for higher level checks
    return \@outcomes;
  }

  #need a valid breed for consistency checks
  my $b = $self->breed_parser->parse( $breed_attrs->[0]->value );
  return \@outcomes if ( !$b );
  my @breeds = $b->all_breeds;
  push @breeds, $breed_attrs->[0]->id if $breed_attrs->[0]->id;

  my $species_match = $self->ols_lookup->find_match( $species_attrs->[0]->id,
    $self->species_permitted_term, 0 );
  return \@outcomes if ( !$species_match );

  my $valid_parent_lbo_term_for_species =
    $self->choose_species_breed_tree($species_match);

  return \@outcomes if ( !$valid_parent_lbo_term_for_species );

  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    term_iri =>
      "http://purl.obolibrary.org/obo/$valid_parent_lbo_term_for_species",
    ontology_name => "LBO"
  );

  my @mismatched_breeds =
    grep { !$self->ols_lookup->find_match( $_, $pt, 0 ) } @breeds;

  my $outcome =
    Bio::Metadata::Validate::ValidationOutcome->new( attributes => $breed_attrs,
    );
  push @outcomes, $outcome;

  if (@mismatched_breeds) {
    $pt->term_iri('http://purl.obolibrary.org/obo/LBO_0000000');
    @mismatched_breeds =
      map { $self->ols_lookup->find_match( $_, $pt, 0 ) }
      @mismatched_breeds;    #get terms
    @mismatched_breeds =
      map { $_->{label} . ' (' . $_->{short_form} . ')' }
      @mismatched_breeds;    #make text from them
    @mismatched_breeds =
      sort keys { map { $_ => 1 } @mismatched_breeds };    #uniq the text

    my $species = $species_match->{label};

    $outcome->outcome('error');
    $outcome->message(
      "These breeds do not match the animal species ($species): "
        . join( ', ', @mismatched_breeds ) );
  }
  else {
    $outcome->outcome('pass');
  }

  return \@outcomes;
}

sub choose_species_breed_tree {
  my ( $self, $species_match ) = @_;

  if ( $self->get_species_to_lbo_breed_mapping( $species_match->{short_form} ) )
  {
    return $self->get_species_to_lbo_breed_mapping(
      $species_match->{short_form} );
  }

  for my $faang_species_id ( $self->keys_species_to_lbo_breed_mapping ) {
    my $pt = Bio::Metadata::Rules::PermittedTerm->new(
      term_iri      => "http://purl.obolibrary.org/obo/$faang_species_id",
      ontology_name => "NCBITaxon"
    );

    my $species_match =
      $self->ols_lookup->find_match( $species_match->{short_form}, $pt, 0 );

    if ($species_match) {
      return $self->get_species_to_lbo_breed_mapping($faang_species_id);
    }
  }

  return undef;
}

__PACKAGE__->meta->make_immutable;

1;
