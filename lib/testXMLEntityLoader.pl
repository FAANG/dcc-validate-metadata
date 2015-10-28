use strict;
use warnings;
use Bio::Metadata::ValidateSchema::EntityValidator;
use JSON;

my $loader = Bio::Metadata::Loader::XMLEntityLoader->new();

my $o=$loader->load('experiment.xml');

my $JSON = JSON->new->utf8;
$JSON->convert_blessed(1);

my $json_text = $JSON->pretty->encode($o);
print "h\n";
