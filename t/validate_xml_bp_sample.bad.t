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

my $o=$loader->load("$data_dir/BPsample_bad.xml");

isa_ok($o, "Bio::Metadata::Entity");

my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => $schema_file,
								    'entity' => $o
								   );

isa_ok($validator, "Bio::Metadata::ValidateSchema::EntityValidator");

my $outcomeset=$validator->validate();

isa_ok($outcomeset, "Bio::Metadata::ValidateSchema::ValidationOutcomeSet");

foreach my $outcome ($outcomeset->all_outcomes) {
  isa_ok($outcome, "Bio::Metadata::ValidateSchema::ValidationOutcome");
  print $outcome->entity->id,"\t",$outcome->entity->entity_type,"\t",$outcome->outcome,"\n";
  foreach my $warning ($outcome->all_warnings) {
    isa_ok($warning, "Bio::Metadata::ValidateSchema::Warning");
    print "\t",$warning->message,"\n";
  }
}

done_testing();
