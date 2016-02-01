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
use Bio::Metadata::Loader::JSONRuleSetLoader;
use Bio::Metadata::Loader::JSONEntityLoader;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Reporter::ExcelReporter;

my $data_dir = "$Bin/data";

my $output = "test_out.xlsx";

my $rule_set = Bio::Metadata::Loader::JSONRuleSetLoader->new()
  ->load("$data_dir/test_good_rule_set.json");

my $test_data =
  Bio::Metadata::Loader::JSONEntityLoader->new()->load("$data_dir/test_data.json");

my $validator =
  Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

my ( $entity_status, $entity_outcomes, $attribute_status, $attribute_outcomes )
  = $validator->check_all($test_data);

my $reporter = Bio::Metadata::Reporter::ExcelReporter->new( file_path => $output );


$reporter->report(
    entities           => $test_data,
    entity_status      => $entity_status,
    entity_outcomes    => $entity_outcomes,
    attribute_status   => $attribute_status,
    attribute_outcomes => $attribute_outcomes
);

unlink($output);

ok(1);
done_testing();

