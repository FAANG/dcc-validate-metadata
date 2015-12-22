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
my $schema_file="$Bin/../json_schemas/Sample.schema.dev.json";

my $loader = Bio::Metadata::Loader::XMLSampleLoader->new();

my $o=$loader->load("$data_dir/sample_good.xml");

isa_ok($o, "Bio::Metadata::Entity");

my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entity' => $o
								   );

isa_ok($validator, "Bio::Metadata::ValidateSchema::EntityValidator");

my $outcomeset=$validator->validate();

isa_ok($outcomeset, "Bio::Metadata::ValidateSchema::ValidationOutcomeSet");

my $outcome= $outcomeset->all_outcomes();

foreach my $outcome ($outcomeset->all_outcomes) {
  is( $outcome->outcome, 'pass');
  is( $outcome->entity->entity_type, 'SAMPLE');
}

done_testing();
