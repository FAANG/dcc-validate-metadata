#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../../lib";

use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Bio::Metadata::BioSample::SampleTab;

my $data_dir = "$Bin/../data/";

my $sampletab= Bio::Metadata::BioSample::SampleTab->new();
isa_ok($sampletab, "Bio::Metadata::BioSample::SampleTab");

$sampletab->read("$data_dir/Excel/sampleset.bsamples.xlsx");

my $msi=$sampletab->report_msi;
my $scd=$sampletab->report_scd;

print $msi;
print $scd;

done_testing();






