use strict;
use warnings;

use XML::Simple;
use Bio::Metadata::XML;

my $XML = Bio::Metadata::XML->new();

my $data_hash=$XML->get_hash_from_file("../experiment/experiment.xml");

$XML->set_id($data_hash);

$XML->set_type($data_hash);

$XML->set_links($data_hash);

#$XML->add_link();

$XML->set_attributes($data_hash);


print "hello\n";
