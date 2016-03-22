#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Validate::Support::FaangBreedParser;

my $parser = Bio::Metadata::Validate::Support::FaangBreedParser->new();

lexer_tests();
#compliance_tests();
#non_compliance_tests();


done_testing();

sub non_compliance_tests {
  my $l_dangle_br = 'BreedA sire x ((BreedA sire x BreedB dam) dam';
  my $l_dangle_br_out = $parser->parse($l_dangle_br);
  is_deeply(
    $l_dangle_br_out,{},'left dangling bracket'
  );

  my $r_dangle_br = 'BreedA sire x (BreedA sire x BreedB dam)) dam';
  my $r_dangle_br_out = $parser->parse($r_dangle_br);
  is_deeply(
    $r_dangle_br_out,
    {},
    'right dangling bracket'
  )
}

#these tests cover use cases that strictly meet the spec
sub compliance_tests {
  #
  my $pure_bred     = 'BreedP';
  my $pure_bred_out = $parser->parse($pure_bred);
  is_deeply( $pure_bred_out, { breeds => ['BreedP'] }, 'pure bred' );

  my $simple_cross     = 'BreedA sire x BreedB dam';
  my $simple_cross_out = $parser->parse($simple_cross);
  is_deeply(
    $simple_cross_out,
    {
      sire => 'BreedA',
      dam  => 'BreedB'
    },
    'simple cross'
  );

  my $back_cross     = 'BreedA sire x (BreedA sire x BreedB dam) dam';
  my $back_cross_out = $parser->parse($back_cross);
  is_deeply(
    $back_cross_out,
    {
      sire => 'BreedA',
      dam  => {
        sire => 'BreedA',
        dam  => 'BreedB'
      }
    },
    'back cross'
  );

  my $mixed_breeds     = 'Breed A, BreedB, BreedC';
  my $mixed_breeds_out = $parser->parse($mixed_breeds);
  is_deeply( $mixed_breeds_out, { breeds => [ 'Breed A', 'BreedB', 'BreedC' ], },
    'mixed_breeds' );
}

#test the lexer which underpins the parser
sub lexer_tests {
  my $lexer_test = 'BreedA sire x (BreedA sire x BreedB dam) dam';
  my @lt_out     = $parser->_lexer($lexer_test);
  is_deeply(
    \@lt_out,
    [
      'BreedA', 'sire',   'x',   '(', 'BreedA', 'sire',
      'x',      'BreedB', 'dam', ')', 'dam'
    ],
    'lexer test'
  );

  my $padded_lexer_test = ' BreedA sire   x (   BreedA sire x BreedB dam) dam';
  my @plt_out     = $parser->_lexer($padded_lexer_test);
  is_deeply(
    \@plt_out,
    [
      'BreedA', 'sire',   'x',   '(', 'BreedA', 'sire',
      'x',      'BreedB', 'dam', ')', 'dam'
    ],
    'lexer test with white space padding'
  );

  my $annoying_brackets = 'Criollo (Uruguay)';
  my @annoying_brackets_out     = $parser->_lexer($annoying_brackets);
  is_deeply(
    \@annoying_brackets_out,
    [
      'Criollo', '(Uruguay)'
    ],
    'lexer test with non-significant brackets'
  );

  my $very_annoying_brackets = 'Criollo (Uruguay) dam x breed b sire';
  my @very_annoying_brackets_out     = $parser->_lexer($very_annoying_brackets);
  is_deeply(
    \@very_annoying_brackets_out,
    [
      'Criollo', '(Uruguay)', 'dam', 'x', 'breed', 'b', 'sire'
    ],
    'lexer test with non-significant brackets'
  );
}
