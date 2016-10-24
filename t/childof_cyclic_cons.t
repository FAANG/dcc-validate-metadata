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
    id          => 'A',
    attributes => [
      {
        name       => 'Child Of',
        value      => 'B',
      },    #pig biosamples parent
    ]
  );

  my $pigparent = Bio::Metadata::Entity->new(
    id          => 'B',
    attributes => [
      {
        name       => 'Child Of',
        value      => 'C',
      },    #pig biosamples parent
    ]
  );

  my $outcomes = $cons_check->check_entity( $e, {'B' => $pigparent});

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'pass',
        attributes => $e->get_attribute(0)
        )
    ],
    'pass for child A with parent B and grandparent C'
  );
}

sub test_fail {
  my $e = Bio::Metadata::Entity->new(
    id          => 'A',
    attributes => [
      {
        name       => 'Child Of',
        value      => 'B',
      },    #pig biosamples parent
    ]
  );

  my $pigparent = Bio::Metadata::Entity->new(
    id          => 'B',
    attributes => [
      {
        name       => 'Child Of',
        value      => 'A',
      },    #pig species
    ]
  );


  my $outcomes = $cons_check->check_entity( $e, {'B' => $pigparent});

  is_deeply(
    $outcomes,
    [
      Bio::Metadata::Validate::ValidationOutcome->new(
        outcome    => 'error',
        message    => 'The parent of child (A) lists this child as its own parent: A',
        attributes => $e->get_attribute(0)
        )

    ],
    'error for child A with parent B whos parent is child A'
  );
}