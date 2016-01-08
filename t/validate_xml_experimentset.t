#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use JSON;
use Data::Dumper;

use Bio::Metadata::Loader::XMLExperimentLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use Test::More;
use Bio::Metadata::Reporter::ExcelReporter;

my $data_dir = "$Bin/data";
my $schema_file="$Bin/../json_schemas/Experiment.schema.dev.json";

my $output = "test_out.experimentset.bad.xlsx";

my $loader = Bio::Metadata::Loader::XMLExperimentLoader->new();

my $o=$loader->load("$data_dir/XML/experimentset_bad.xml");

isa_ok($o, "ARRAY");

my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entityarray' => $o
								   );

isa_ok($validator, "Bio::Metadata::ValidateSchema::EntityValidator");

my ( $entity_status, $entity_outcomes, $attribute_status, $attribute_outcomes )=$validator->validate_all($o);

my $reporter = Bio::Metadata::Reporter::ExcelReporter->new( file_path => $output );

$reporter->report(
    entities           => $o,
    entity_status      => $entity_status,
    entity_outcomes    => $entity_outcomes,
    attribute_status   => $attribute_status,
    attribute_outcomes => $attribute_outcomes
);

done_testing();

