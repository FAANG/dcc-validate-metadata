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
test_bad();
test_not_json();
done_testing();

sub test_good {
  my $file = "$data_dir/test_good_rule_set.json";
  my $rule_set;
  
  lives_ok {$rule_set = $loader->load($file) } 'does not die when reading good rule set';
  ok($rule_set,'rule set should exist');

  

} 

sub test_bad {
  my $file = "$data_dir/test_bad_rule_set.json";
  my $rule_set;
  
  dies_ok {$rule_set = $loader->load($file) } 'does die when reading bad rule set';
}

sub test_not_json {
  my $file = "$data_dir/test.not_json";
  my $rule_set;
  
  dies_ok {$rule_set = $loader->load($file) } 'does die when reading invalid json';
}