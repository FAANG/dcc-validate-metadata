#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Test::More;

my $data_dir = "$Bin/data";

use Bio::Metadata::Entity;
use Bio::Metadata::Attribute;

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
        { name => 'weight', value => '50',   units => 'g' },
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
        { name => 'weight', value => '50',   units => 'g',  uri => undef },

    ]
};
is_deeply( $actural_sh, $expected_sh, 'Entity to hash' );

my $actual_organised_attrs  = $sample->organised_attr();
my $expected_organised_attr = {
    sex =>
      [ Bio::Metadata::Attribute->new( name => 'sex', value => 'female' ), ],
    tissue => [
        Bio::Metadata::Attribute->new(
            name  => 'tissue',
            value => 'muscle',
            uri   => 'http://purl.obolibrary.org/obo/UBERON_0002385'
        ),
    ],
    weight => [
        Bio::Metadata::Attribute->new(
            name  => 'weight',
            value => '0.05',
            units => 'kg'
        ),
        Bio::Metadata::Attribute->new(
            name  => 'weight',
            value => '50',
            units => 'g'
        ),
    ],
};

is_deeply( $actual_organised_attrs, $expected_organised_attr,
    'Organise entity attributes' );

done_testing();
