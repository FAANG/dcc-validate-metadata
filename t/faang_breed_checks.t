#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Faang::FaangBreedParser;
use Bio::Metadata::Faang::FaangBreedValidator;
use Bio::Metadata::Faang::FaangBreed;
use Bio::Metadata::Attribute;
use Bio::Metadata::Rules::Rule;

my $parser = Bio::Metadata::Faang::FaangBreedParser->new();

lexer_tests();
compliance_tests();
non_compliance_tests();
what_the_heck_tests();
test_validator();

done_testing();

#test the validator
sub test_validator {
  my $v = Bio::Metadata::Faang::FaangBreedValidator->new();
  my $r = Bio::Metadata::Rules::Rule->new(
    type        => 'faang_breed',
    valid_terms => Bio::Metadata::Rules::PermittedTerm->new(
      ontology_name     => 'LBO',
      allow_descendants => 1,
      leaf_only         => 1,
      include_root      => 0,
      term_iri          => 'http://purl.obolibrary.org/obo/LBO_0000000',
    )
  );

  my @valid_values = (
    [ 'Charolais',                                           'LBO_0000073' ],
    [ 'Charolais,Holstein',                                  'LBO_0001036' ],
    [ 'Charolais, Holstein',                                 'LBO_0001036' ],
    [ 'Charolais sire x Holstein dam',                       'LBO_0001036' ],
    [ '(Charolais sire x Holstein dam) sire x Holstein dam', 'LBO_0001036' ],
    [ 'Holstein sire x (Charolais sire x Holstein dam) dam', 'LBO_0001036' ],
  );

  for my $val (@valid_values) {
    my $a = Bio::Metadata::Attribute->new(
      value      => $val->[0],
      id         => $val->[1],
      source_ref => 'LBO'
    );
    my $o = $v->validate_attribute( $r, $a );
    is( $o->outcome, 'pass', 'valid value: ' . $val->[0] );
  }

  my @invalid_values = (
    [ 'Not a breed name',       'NOTABREEDID' ],    #won't match in LBO
    [ 'Holstein,NOTABREEDNAME', 'LBO_0001036' ],    #part won't match in LBO
    [
'((Charolais sire x Holstein dam) sire x Holstein dam) sire x Holstein dam',
      'LBO_0001036'
    ],                                              #should just be a list
    [ '(Charolais,Holstein) sire x Holstein dam', 'LBO_0001036' ]
    ,                                               #should just be a list
    [ 'Holstein sire x Holstein dam', 'LBO_0001036' ]
    ,    #should just be a single value
  );
  for my $val (@invalid_values) {
    my $a = Bio::Metadata::Attribute->new(
      value      => $val->[0],
      id         => $val->[1],
      source_ref => 'LBO'
    );
    my $o = $v->validate_attribute( $r, $a );
    is( $o->outcome, 'error', 'invalid value: ' . $val->[0] );
  }

  my @warn_values = (
    [ 'Holstein sire x Charolais dam', 'LBO_0000073' ]
    ,    #pure breed id and cross nomenclature
    [ 'Holstein', 'LBO_0000073' ],    #Charolais breed id and Holstein value

  );
  for my $val (@warn_values) {
    my $a = Bio::Metadata::Attribute->new(
      value      => $val->[0],
      id         => $val->[1],
      source_ref => 'LBO'
    );
    my $o = $v->validate_attribute( $r, $a );
    is( $o->outcome, 'warning', 'warned value: ' . $val->[0] );
  }
}

# tests that go beyond the written spec, but should be within the parsers capabilities
sub what_the_heck_tests {
  my $quad_cross_breed     = '(A sire x B dam) sire x (C sire x D dam) dam';
  my $quad_cross_breed_out = $parser->parse($quad_cross_breed);
  is_deeply(
    $quad_cross_breed_out,
      Bio::Metadata::Faang::FaangBreed->new(
        sire => Bio::Metadata::Faang::FaangBreed->new( sire => 'A', dam => 'B' ),
        dam  => Bio::Metadata::Faang::FaangBreed->new( sire => 'C', dam => 'D' ),
      )
    ,
    'quad cross'
  );

  my $heavy_nesting =
    'A sire x (B sire x (C sire x (D sire x E dam) dam) dam) dam';
  my $heavy_nesting_out = $parser->parse($heavy_nesting);
  is_deeply(
    $heavy_nesting_out,
    Bio::Metadata::Faang::FaangBreed->new(
      sire => 'A',
      dam  => Bio::Metadata::Faang::FaangBreed->new(
        sire => 'B',
        dam  => Bio::Metadata::Faang::FaangBreed->new(
          sire => 'C',
          dam  => Bio::Metadata::Faang::FaangBreed->new(
            sire => 'D',
            dam  => 'E',
          ),
        ),
      ),
    ),
    'heavily nested breed info'
  );
}

sub non_compliance_tests {
  my $l_dangle_br     = 'BreedA sire x ((BreedA sire x BreedB dam) dam';
  my $l_dangle_br_out = $parser->parse($l_dangle_br);
  is_deeply( $l_dangle_br_out, {}, 'left dangling bracket' );

  my $r_dangle_br     = 'BreedA sire x (BreedA sire x BreedB dam)) dam';
  my $r_dangle_br_out = $parser->parse($r_dangle_br);
  is_deeply( $r_dangle_br_out, {}, 'right dangling bracket' );
}

#these tests cover use cases that strictly meet the spec
sub compliance_tests {
  #
  my $pure_bred     = 'BreedP';
  my $pure_bred_out = $parser->parse($pure_bred);
  is_deeply( $pure_bred_out, Bio::Metadata::Faang::FaangBreed->new(breeds => ['BreedP'] ), 'pure bred' );

  my $simple_cross     = 'BreedA sire x BreedB dam';
  my $simple_cross_out = $parser->parse($simple_cross);
  is_deeply(
    $simple_cross_out,
    Bio::Metadata::Faang::FaangBreed->new(
      sire => 'BreedA',
      dam  => 'BreedB'
    ),
    'simple cross'
  );

  my $back_cross     = 'BreedA sire x (BreedA sire x BreedB dam) dam';
  my $back_cross_out = $parser->parse($back_cross);
  is_deeply(
    $back_cross_out,
    Bio::Metadata::Faang::FaangBreed->new(
      sire => 'BreedA',
      dam  => Bio::Metadata::Faang::FaangBreed->new(
        sire => 'BreedA',
        dam  => 'BreedB'
      )
    ),
    'back cross'
  );

  my $mixed_breeds     = 'Breed A, BreedB, BreedC';
  my $mixed_breeds_out = $parser->parse($mixed_breeds);
  is_deeply( $mixed_breeds_out,
    Bio::Metadata::Faang::FaangBreed->new( breeds => [ 'Breed A', 'BreedB', 'BreedC' ], ),
    'mixed_breeds' );

  my $annoying_brackets     = 'Criollo (Uruguay)';
  my $annoying_brackets_out = $parser->parse($annoying_brackets);
  is_deeply(
    $annoying_brackets_out,
    Bio::Metadata::Faang::FaangBreed->new( breeds => ['Criollo (Uruguay)'] ),
    'pure breed with brackets in name'
  );

  my $very_annoying_brackets     = 'Criollo (Uruguay) sire x breed b dam';
  my $very_annoying_brackets_out = $parser->parse($very_annoying_brackets);
  is_deeply(
    $very_annoying_brackets_out,
    Bio::Metadata::Faang::FaangBreed->new(
      sire => 'Criollo (Uruguay)',
      dam  => 'breed b',
    ),
    'cross breed with brackets in the name'
  );
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
  my @plt_out           = $parser->_lexer($padded_lexer_test);
  is_deeply(
    \@plt_out,
    [
      'BreedA', 'sire',   'x',   '(', 'BreedA', 'sire',
      'x',      'BreedB', 'dam', ')', 'dam'
    ],
    'lexer test with white space padding'
  );

  my $very_annoying_brackets     = 'Criollo (Uruguay) sire x breed b dam';
  my @very_annoying_brackets_out = $parser->_lexer($very_annoying_brackets);
  is_deeply(
    \@very_annoying_brackets_out,
    [ 'Criollo', '(Uruguay)', 'sire', 'x', 'breed', 'b', 'dam' ],
    'lexer test breed with brackets in the name'
  );
}
