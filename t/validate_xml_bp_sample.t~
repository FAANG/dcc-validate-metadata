#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Bio::Metadata::Loader::XMLSampleLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;

my $data_dir = "$Bin/data";
my $schema_file="$Bin/../json_schemas/BlueprintSample.schema.json";

my $loader = Bio::Metadata::Loader::XMLSampleLoader->new();

my $o=$loader->load("$data_dir/BPsample_good.xml");


my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entity' => $o
								   );

$validator->validate();


