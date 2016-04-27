#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Entity;
use Bio::Metadata::Faang::FaangBreedSpeciesCheck;
use Bio::Metadata::Validate::ValidationOutcome;

my $cons_check = Bio::Metadata::Faang::FaangBreedSpeciesCheck->new();
test_pass();
test_sub_species_pass();
test_fail();
done_testing();

sub test_pass {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'breed',
        value      => 'Corsican',
        id         => 'LBO_0000975',
        source_ref => 'LBO'
      },    #goat breed
      {
        name       => 'Organism',
        value      => 'Capra hircus',
        id         => 'NCBITaxon_9925',
        source_ref => 'NCBITaxon'
      },    #goat species
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {} );

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'pass',
        attributes => $e->get_attribute(0)
        )
    ],
    'pass for goat + goat breed (Corsican)'
  );
}

sub test_sub_species_pass {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'breed',
        value      => 'Duroc',
        id         => 'LBO_0000358',
        source_ref => 'LBO'
      },    #pig breed
      {
        name       => 'Organism',
        value      => 'Sus scrofa domesticus',
        id         => 'NCBITaxon_9825',
        source_ref => 'NCBITaxon'
      },    #pig sub species
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {} );

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'pass',
        attributes => $e->get_attribute(0)
        )

    ],
    'pass for pig breed + sus scrofa domesticus'
  );
}

sub test_fail {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'breed',
        value      => 'Corsican',
        id         => 'LBO_0000975',
        source_ref => 'LBO'
      },    #goat breed
      {
        name       => 'Organism',
        value      => 'Bos taurus',
        id         => 'NCBITaxon_9913',
        source_ref => 'NCBITaxon'
      },    #cattle species
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {} );

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'error',
        message    => 'These breeds do not match the animal species (Bos taurus): Corsican (LBO_0000975)',
        attributes => $e->get_attribute(0)
        )

    ],
    'error for cattle + goat breed'
  );
}
