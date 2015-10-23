use strict;
use warnings;

use XML::Simple;
use Bio::Metadata::XML;

my $XML = Bio::Metadata::XML->new();

my $data_hash=$XML->get_hash_from_file("/Users/ernesto/scripts/validate/experiment/experiment.xml");

$XML->set_id($data_hash);

$XML->set_type($data_hash);

print "hello\n";
