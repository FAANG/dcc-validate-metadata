use strict;
use warnings;
use Bio::Metadata::Loader::XMLExperimentLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;

my $loader = Bio::Metadata::Loader::XMLExperimentLoader->new();

my $o=$loader->load('experiment.xml');


my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => '/Users/ernesto/scripts/validate/lib/Bio/Metadata/ValidateSchema/Schemas/BlueprintExperiment.schema.json',
								    'entity' => $o
								   );

$validator->validate();


