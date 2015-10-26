use strict;
use warnings;
use Bio::Metadata::Loader::XMLEntityLoader;


my $loader = Bio::Metadata::Loader::XMLEntityLoader->new();

$loader->load('experiment.xml');

print "h\n";
