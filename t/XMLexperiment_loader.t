#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use JSON;
use Data::Dumper;

use Bio::Metadata::Loader::XMLExperimentLoader;
use Test::More;

my $data_dir = "$Bin/data";

my $loader = Bio::Metadata::Loader::XMLExperimentLoader->new();

my $o=$loader->load("$data_dir/XML/experiment_good.xml");

isa_ok($o, "ARRAY");

done_testing();

