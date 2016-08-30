#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Test::More;

use Bio::Metadata::Entity;
use Bio::Metadata::Faang::FaangChildOfCyclicCheck;
use Bio::Metadata::Validate::ValidationOutcome;

my $cons_check = Bio::Metadata::Faang::FaangChildOfCyclicCheck->new();
test_pass();
test_fail();
done_testing();


sub test_pass { 
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
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
      },    #pig species
    ]
  );

  my $outcomes = $cons_check->check_entity( {'CHILD1' => $e}, {'PIGPARENT1' => $pigparent});

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

sub test_fail {
  my $e = Bio::Metadata::Entity->new(
    attributes => [
      {
        name       => 'Organism',
        value      => 'Sus scrofa',
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
      },
      {
        name       => 'Child Of',
        value      => 'CHILD1',
      },    #pig species
    ]
  );


  my $outcomes = $cons_check->check_entity( {'CHILD1' => $e}, {'PIGPARENT1' => $pigparent});

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'error',
        message    => 'The parent of child (CHILD1) lists this child as its own parent: CHILD1',
        attributes => $e->get_attribute(0)
        )

    ],
    'error for pig with a chicken parent'
  );
}