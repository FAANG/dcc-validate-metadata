#!/usr/bin/env perl
use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Validate::Support::BioSDLookup;
use Bio::Metadata::Entity;

my $lookup = Bio::Metadata::Validate::Support::BioSDLookup->new();

{
  my $id     = 'SAMEA676028';
  my $sample = $lookup->fetch_sample($id);
  ok( $sample, "got sample when looking up a valid id" );
}
{
  my $id     = 'I_AM_NOT_A_SAMPLE';
  my $sample = $lookup->fetch_sample($id);
  ok( !defined $sample, "got undef when looking up an invalid id" );
}
{
  my $id     = 'SAMEA676028';
  my $sample = $lookup->fetch_sample($id);

  my $expected = Bio::Metadata::Entity->new(
    id          => 'source GSM754269 1',
    synonyms    => [$id],
    entity_type => 'sample',
    attributes  => [
      {
        'value' =>
          'Gene expression after 4hr in 2ug/ml BSP-II-treated DT40 cell',
        'name' => 'Sample Description',

      },
      {
        'source_ref' => 'NCBI Taxonomy',
        'value'      => 'Gallus gallus',
        'name'       => 'Organism',
        'id'         => '9031',
        'uri'        => 'http://www.ncbi.nlm.nih.gov/taxonomy/',
      },
      {

        'value' => 'DT40',
        'name'  => 'strain',

      },
      {

        'value' => 'DT40 cell, 4hr, 2ug/ml, replicate 1',
        'name'  => 'Sample_source_name',
      },
      {
        'value' => "2011-07-05T23:00:00+00:00",
        'name' => 'BioSamples release date',
        'allow_further_validation' => undef,
      },
      {
        'value' => "2014-02-03T19:06:04+00:00",
        'name' => 'BioSamples update date',
        'allow_further_validation' => undef,
      }
    ]
  );

  is_deeply( $sample, $expected,
    "BioSample converted to Bio::Metadata::Entity" );
}
done_testing();
