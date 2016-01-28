#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Bio::Metadata::Loader::TSVLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use Data::Dumper;
use Test::More;

my $data_dir = "$Bin/data";
my $schema_file="$Bin/../json_schemas/Sample.schema.dev.json";

my $loader = Bio::Metadata::Loader::TSVLoader->new();

my $o=$loader->load("$data_dir/TSV/sampleset.tsv");

isa_ok($o, "ARRAY");

done_testing();
