use strict;
use warnings;
use Bio::Metadata::Loader::XMLSampleLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;

my $loader = Bio::Metadata::Loader::XMLSampleLoader->new();

my $o=$loader->load('sample.xml');


my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => '/Users/ernesto/scripts/validate/lib/Bio/Metadata/ValidateSchema/Schemas/BlueprintSample.schema.json',
								    'entity' => $o
								   );

$validator->validate();


