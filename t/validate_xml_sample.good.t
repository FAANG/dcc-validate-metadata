#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use lib "/Users/ernesto/test_json/json-validator/lib";

use Bio::Metadata::Loader::XMLSampleLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;
use Test::More;
use Bio::Metadata::Reporter::ExcelReporter;

my $data_dir = "$Bin/data";
my $schema_file="$Bin/../json_schemas/Sample.schema.dev.json";

my $loader = Bio::Metadata::Loader::XMLSampleLoader->new();

my $o=$loader->load("$data_dir/XML/sample_good.xml");

isa_ok($o, "Bio::Metadata::Entity");

my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entity' => $o,
									'selector' => "BIOMATERIAL_TYPE"
								   );

isa_ok($validator, "Bio::Metadata::ValidateSchema::EntityValidator");

my ( $outcome_overall, $outcomes )=$validator->validate($o);

is( $outcome_overall, 'pass', 'pass outcome expected' );

done_testing();
