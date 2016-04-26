#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;
use Test::Exception;
use Bio::Metadata::Loader::JSONRuleSetLoader;

my $data_dir = "$Bin/data";

my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();

test_good();
test_good_with_cons_check();
test_bad();
test_not_json();
test_dodgy_cons();
done_testing();

sub test_good {
  my $file = "$data_dir/test_good_rule_set.json";
  my $rule_set;

  lives_ok { $rule_set = $loader->load($file) }
  'does not die when reading good rule set';
  ok( $rule_set, 'rule set should exist' );
}

sub test_good_with_cons_check {
  my $file = "$data_dir/test_good_rule_set_with_cons_check.json";
  my $rule_set;

  lives_ok { $rule_set = $loader->load($file) }
  'does not die when reading good rule set with conscheck';
  ok( $rule_set, 'rule set should exist' );
  if ($rule_set) {
    ok(
      $rule_set->get_rule_group(1)
        ->get_consistency_check('faang_breed_species_check'),
      'consistency check should exist'
    );
    isa_ok(
      $rule_set->get_rule_group(1)
        ->get_consistency_check('faang_breed_species_check'),
      'Bio::Metadata::Faang::FaangBreedSpeciesCheck'
    );
  }
}

sub test_bad {
  my $file = "$data_dir/test_bad_rule_set.json";
  my $rule_set;

  dies_ok { $rule_set = $loader->load($file) }
  'does die when reading bad rule set';
}

sub test_dodgy_cons {
  my $file = "$data_dir/test_bad_cons_rule_set.json";
  my $rule_set;

  dies_ok { $rule_set = $loader->load($file) }
  'does die when reading rule set with bad consistency check';
}

sub test_not_json {
  my $file = "$data_dir/test.not_json";
  my $rule_set;

  dies_ok { $rule_set = $loader->load($file) }
  'does die when reading invalid json';
}
