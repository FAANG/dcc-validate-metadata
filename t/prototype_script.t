#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use JSON;
use Test::More;
use Test::Exception;
use autodie;
use Bio::Metadata::Loader::RuleSetLoader;
use Bio::Metadata::Loader::EntityLoader;
use Bio::Metadata::Validate::EntityValidator;

my $data_dir = "$Bin/data";

my $rule_set = Bio::Metadata::Loader::RuleSetLoader->new()
  ->load("$data_dir/test_good_rule_set.json");

my $test_data =
  Bio::Metadata::Loader::EntityLoader->new()->load("$data_dir/test_data.json");
  
my $validator = Bio::Metadata::Validate::EntityValidator->new(rule_set => $rule_set);

my ($entity_status,$entity_outcomes) = $validator->check_all($test_data);

done_testing();

