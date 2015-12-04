#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Bio::Metadata::Loader::XMLSampleLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;
use Test::More;

my $data_dir = "$Bin/data";
my $schema_file="$Bin/../json_schemas/BlueprintSample.schema.dev.json";

my $loader = Bio::Metadata::Loader::XMLSampleLoader->new();

my $o=$loader->load("$data_dir/BPsampleset_good.xml");

isa_ok($o, "ARRAY");

my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entityarray' => $o
								   );

isa_ok($validator, "Bio::Metadata::ValidateSchema::EntityValidator");

$validator->validate();

done_testing();
