#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Test::More;

my $data_dir = "$Bin/data";

use Bio::Metadata::Entity;

my $sample = Bio::Metadata::Entity->new(
    id          => 'bob',
    entity_type => 'sample',
    attributes  => [
        { name => 'sex', value => 'female' },
        {
            name  => 'tissue',
            value => 'muscle',
            uri   => 'http://purl.obolibrary.org/obo/UBERON_0002385'
        },
        { name => 'weight', value => '0.05', units => 'kg' },
    ],
);

my $actural_sh  = $sample->to_hash();
my $expected_sh = {
    id          => 'bob',
    entity_type => 'sample',
    attributes  => [
        { name => 'sex', value => 'female', units => undef, uri => undef },
        {
            name  => 'tissue',
            value => 'muscle',
            units => undef,
            uri   => 'http://purl.obolibrary.org/obo/UBERON_0002385'
        },
        { name => 'weight', value => '0.05', units => 'kg', uri => undef },
    ]
};
is_deeply($actural_sh,$expected_sh,'Entity to hash');

done_testing();
