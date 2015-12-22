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

my $o=$loader->load("$data_dir/sample_bad.xml");

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
  is( $outcome->outcome, 'warning');
  is( $outcome->entity->entity_type, 'SAMPLE');	
  foreach my $warning ($outcome->all_warnings) {
	is ($warning->message, "ATTRIBUTE-NAME:MOLECULE;VALUE:RNA	oneOf failed: ([0] /MOLECULE: Not in enum list: total RNA, polyA RNA, cytoplasmic RNA, nuclear RNA, genomic DNA, protein, other.)")
  }
}

done_testing();
