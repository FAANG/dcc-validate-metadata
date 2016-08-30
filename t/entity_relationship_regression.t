#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
use Test::Exception;
use Data::Dumper;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Bio::Metadata::Entity;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Faang::FaangChildOfSpeciesCheck;

my $entities = [
  Bio::Metadata::Entity->new(
    id         => 'A',
    attributes => [
      { name => 'Child of', value => 'not provided' },
      { name => 'Organism', value => 'chicken', id => 1 }
    ],
  ),
  Bio::Metadata::Entity->new(
    id         => 'B',
    attributes => [
      { name => 'Child of', value => 'A' },
      { name => 'Organism', value => 'chicken', id => 1 }
    ]
  ),
  Bio::Metadata::Entity->new(
    id         => 'C',
    attributes => [
      { name => 'Child of', value => 'X' },
      { name => 'Organism', value => 'chicken', id => 1 }
    ]
  ),
];

my $rule_set = Bio::Metadata::Rules::RuleSet->new(
  name        => 'test_rs',
  rule_groups => [
    {
      name  => 'test_rg',
      rules => [
        {
          name      => 'Child of',
          type      => 'relationship',
          mandatory => 'optional'
        },
        {
          name      => 'Organism',
          type      => 'text',
          mandatory => 'mandatory'
        }
      ],
      consistency_checks => {
        faang_childof_species_check =>
          Bio::Metadata::Faang::FaangChildOfSpeciesCheck->new(),
        faang_childof_cyclic_check =>
          Bio::Metadata::Faang::FaangChildOfCyclicCheck->new(),
      },
    }
  ]
);

my $validator =
  Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

lives_ok { $validator->check_all($entities) }
'child of species check does not die with missing values or incorrect values ';

done_testing();
