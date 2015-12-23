#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use JSON;
use Test::More;
use autodie;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Loader::JSONRuleSetLoader;
use Bio::Metadata::Loader::XMLSampleLoader;
use Bio::Metadata::Reporter::ExcelReporter;

my $data_dir = "$Bin/data";

my $output = "test_out.xlsx";

my $rule_set = Bio::Metadata::Loader::JSONRuleSetLoader->new()->load("$data_dir/RULES/sample_primarytissue_rules.json");
  
my $loader = Bio::Metadata::Loader::XMLSampleLoader->new("attr_links" => "$data_dir/attr_links.json");

my $data=$loader->load("$data_dir/XML/primary_tissue.sampleset_good.xml");

my $validator = Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

my ( $entity_status, $entity_outcomes, $attribute_status, $attribute_outcomes ) = $validator->check_all($data);

my $reporter =  Bio::Metadata::Reporter::ExcelReporter->new( file_path => $output );

$reporter->report(
    entities           => $data,
    entity_status      => $entity_status,
    entity_outcomes    => $entity_outcomes,
    attribute_status   => $attribute_status,
    attribute_outcomes => $attribute_outcomes
);

ok(1);
done_testing();

