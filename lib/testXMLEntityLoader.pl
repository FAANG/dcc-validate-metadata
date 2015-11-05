use strict;
use warnings;
use Bio::Metadata::Loader::XMLEntityLoader;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;
use Data::Dumper;

my $loader = Bio::Metadata::Loader::XMLEntityLoader->new();

my $o=$loader->load('experiment.bad.attr.xml');


my $validator = Bio::Metadata::ValidateSchema::EntityValidator->new(
								    'schema' => '/Users/ernesto/scripts/validate/experiment/experiment.schema.2910.json',
								    'entity' => $o
								   );

$validator->validate();


