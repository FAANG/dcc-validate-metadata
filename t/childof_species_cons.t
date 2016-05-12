#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Entity;
use Bio::Metadata::Faang::FaangChildOfSpeciesCheck;
use Bio::Metadata::Validate::ValidationOutcome;

my $cons_check = Bio::Metadata::Faang::FaangChildOfSpeciesCheck->new();
test_pass_internal();
test_pass_biosamples();
test_fail_internal();
test_fail_biosamples();
done_testing();

sub test_pass_internal {  #FIXME
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
      {
        name       => 'Child Of',
        value      => 'PIGPARENT1',
      },    #pig biosamples parent
    ]
  );

  my $pigparent = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {'PIGPARENT1' => $pigparent});

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'pass',
        attributes => $e->get_attribute(0)
        )
    ],
    'pass for pig child + pig parent internal to submission'
  );
}

sub test_pass_biosamples {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
      {
        name       => 'Child Of',
        value      => 'SAMEA4447547',
      },    #pig biosamples parent
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
    'pass for pig child + pig parent from biosamples'
  );
}

sub test_fail_internal { #FIXME
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
      {
        name       => 'Child Of',
        value      => 'PIGPARENT1',
      },    #pig biosamples parent
      {
        name       => 'Child Of',
        value      => 'CHICKENPARENT2',
      },    #chicken biosamples parent
    ]
  );

  my $pigparent = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
    ]
  );

  my $chickenparent = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Gallus gallus',
        id         => 'NCBITaxon_9031',
        source_ref => 'NCBITaxon'
      },    #pig species
    ]
  );


  my $outcomes = $cons_check->check_entity( $e, {'PIGPARENT1' => $pigparent, 'CHICKENPARENT2' => $chickenparent} );

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'error',
        message    => 'The species of the child (Sus scrofa) does not match one of the parents (Gallus gallus) in the submission',
        attributes => $e->get_attribute(0)
        )

    ],
    'error for pig with a chicken parent'
  );
}

sub test_fail_biosamples {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
        id         => 'NCBITaxon_9823',
        source_ref => 'NCBITaxon'
      },    #pig species
      {
        name       => 'Child Of',
        value      => 'SAMEA4447547',
      },    #pig biosamples parent
      {
        name       => 'Child Of',
        value      => 'SAMEA4447355',
      },    #chicken biosamples parent
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {} );

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'error',
        message    => 'The species of the child (Sus scrofa) does not match one of the parents (Gallus gallus) from BioSamples',
        attributes => $e->get_attribute(0)
        )

    ],
    'error for pig with a chicken parent'
  );
}

