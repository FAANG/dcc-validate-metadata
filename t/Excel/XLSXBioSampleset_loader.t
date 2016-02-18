#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../../lib";

use Bio::Metadata::Loader::XLSXBioSampleLoader;

my $data_dir = "$Bin/../data/";

my $loader = Bio::Metadata::Loader::XLSXBioSampleLoader->new();

my $o = $loader->load("$data_dir/Excel/sampleset.bsamples.xlsx",['animal','specimen','purified cells','cell culture']);

isa_ok($o, "ARRAY");

is_deeply( [map($_->id,@$o)], [qw(H1 H2 S1 S32 S39 C1 C2)],'id method in Entity.pm reports the correct ids for the different Entity objects' );

done_testing();



