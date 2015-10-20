#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Test::More;

my $data_dir = "$Bin/data";

use Bio::Metadata::Entity;
use Bio::Metadata::Attribute;
use Bio::Rules::RuleSet;



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
    
    my $rule_set = Bio::Rules::RuleSet->new(
        name        => 'ruleset_1',
        description => 'a test ruleset',
        rule_groups => [
            {
                name        => 'g1',
                description => 'std',
                rules       => [
                    {
                        name           => 'r1',
                        type           => 'text',
                        mandatory      => 'mandatory',
                        allow_multiple => 0,
                    },
                    {
                        name           => 'r2',
                        type           => 'enum',
                        mandatory      => 'mandatory',
                        allow_multiple => 1,
                    }
                ],
            }
        ],
    );

    my $actual_rule_set_h   = $rule_set->to_hash();
    my $expected_rule_set_h = {
        name        => 'ruleset_1',
        description => 'a test ruleset',
        rule_groups => [
            {
                name        => 'g1',
                description => 'std',
                condition   => undef,
                rules       => [
                    {
                        name           => 'r1',
                        type           => 'text',
                        mandatory      => 'mandatory',
                        allow_multiple => 0,
                    },
                    {
                        name           => 'r2',
                        type           => 'enum',
                        mandatory      => 'mandatory',
                        allow_multiple => 1,
                    }
                ],
            }
        ],
    };
    is_deeply( $actual_rule_set_h, $expected_rule_set_h, 'Create ruleset' );

done_testing();
