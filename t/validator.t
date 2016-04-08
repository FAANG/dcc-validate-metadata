#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Entity;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Validate::EntityValidator;

my $entity = Bio::Metadata::Entity->new(
    id          => '404-E-132-4FE274A',
    entity_type => 'spacecraft',
    attributes  => [
        {
            name  => 'crew_capacity',
            value => '5',
            units => 'cabins',
        },
        {
            name  => 'passenger_capacity',
            value => '18',
            units => 'people',
        },
        { name => 'class',          value => '03-K64-Firefly' },
        { name => 'role',           value => 'transport' },
        { name => 'cargo_capacity', value => 74797, units => 'kg' }

    ]
);

my $rule_set = Bio::Metadata::Rules::RuleSet->new(
    name        => 'spacecraft checklist',
    description => 'a nerdy test checklist',
    rule_groups => [
        {
            name  => 'standard',
            rules => [
                {
                    name      => 'passenger_capacity',
                    type      => 'number',
                    mandatory => 'mandatory',
                },
                {
                    name      => 'crew_capacity',
                    type      => 'number',
                    mandatory => 'mandatory'
                },
                {
                    name      => 'class_id',
                    type      => 'text',
                    mandatory => 'mandatory',
                },
                {
                  name => 'role',
                  type => 'enum',
                  mandatory => 'mandatory',
                  valid_values => [qw(transport warship)],
                }
            ]
        },
        {
            name => 'warships',
            condition =>
'/attributes/*/*[key eq "name" && value eq "role"]/../*[key eq "value" && value eq "warship"]',
            rules => [
                {
                    name           => 'weapon',
                    type           => 'text',
                    mandatory      => 'mandatory',
                    allow_multiple => 1,
                }
            ]
        },
        {
            name => 'transports',
            condition =>
'/attributes/*/*[key eq "name" && value eq "role"]/../*[key eq "value" && value eq "transport"]',
            rules => [
                {
                    name        => 'cargo_capacity',
                    type        => 'number',
                    mandatory   => 'mandatory',
                    valid_units => ['kg'],

                }
            ]
        }
    ]
);

my $v = Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );
my ( $outcome_overall, $outcomes ) = $v->check($entity);

is( $outcome_overall, 'error', 'error outcome expected' );

my @actual_outcomes = map { $_->to_hash } @$outcomes;

my %base_outcome = (
    entity_id   => '404-E-132-4FE274A',
    entity_type => 'spacecraft',
);

my @expected_outcomes = (
    {
        %base_outcome,
        rule_group_name => 'standard',
        outcome         => 'error',
        message         => 'mandatory attribute not present',
        rule            => $rule_set->get_rule_group(0)->get_rule(2)->to_hash,
        attributes      => [],
    },
    {
        %base_outcome,
        rule_group_name => undef,
        outcome         => 'warning',
        message         => 'attribute not in rule set',
        rule            => undef,
        attributes      => [ $entity->get_attribute(2)->to_hash ],
    },
);

is( scalar(@actual_outcomes), 2, "got expected number of validation outcomes" );
is_deeply( \@actual_outcomes, \@expected_outcomes,
    'validation outcomes match expectation' );

$entity->get_attribute(2)->name('class_id');

( $outcome_overall, $outcomes ) = $v->check($entity);

is( $outcome_overall, 'pass', 'pass outcome expected' );

done_testing();
