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

$sampletab->read("$data_dir/Excel/test.xlsx");

$sampletab->print_msi;
$sampletab->print_scd;









