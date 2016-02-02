#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;
use Bio::Metadata::Rules::Condition; 
use Bio::Metadata::Entity;

my $sample = Bio::Metadata::Entity->new(
    id          => 'bob',
    entity_type => 'sample',
    attributes  => [
        { name => 'sex',    value => 'female' },
        { name => 'weight', value => '0.05', units => 'kg' },
        {
            name  => 'tissue',
            value => 'muscle',
            uri   => 'http://purl.obolibrary.org/obo/UBERON_0002385'
        },
        { name => 'weight', value => '50', units => 'g' },
    ],
    links => []
);

my $condition = Bio::Metadata::Rules::Condition->new(
  attribute_value_match => {tissue => ['muscle']}
); 
ok($condition->entity_passes($sample),"Single match");

$condition = Bio::Metadata::Rules::Condition->new(
  attribute_value_match => {tissue => ['ferret','muscle']}
); 
ok($condition->entity_passes($sample),"Single match one of two");

$condition = Bio::Metadata::Rules::Condition->new(
  attribute_value_match => {tissue => ['muscle'],sex => ['male','female']}
); 
ok($condition->entity_passes($sample),"Match two attributes");

$condition = Bio::Metadata::Rules::Condition->new(
  attribute_value_match => {tissue => ['ferret']}
); 
ok(!$condition->entity_passes($sample),"Mismatch one attribute");

$condition = Bio::Metadata::Rules::Condition->new(
  attribute_value_match => {tissue => ['ferret'],sex => ['female']}
); 
ok(!$condition->entity_passes($sample),"Mismatch one attribute, match one");

$condition = Bio::Metadata::Rules::Condition->new(
  dpath_condition => "/attributes/*/*[key eq 'name' && value eq 'tissue']/../*[key eq 'value' && value eq 'muscle']"
); 
ok($condition->entity_passes($sample),"Match a Dpath condition");

$condition = Bio::Metadata::Rules::Condition->new(
  dpath_condition => "/attributes/*/*[key eq 'name' && value eq 'tissue']/../*[key eq 'value' && value eq 'ferret']"
); 
ok(!$condition->entity_passes($sample),"Mismatch a Dpath condition");

$condition = Bio::Metadata::Rules::Condition->new(
  dpath_condition => "/attributes/*/*[key eq 'name' && value eq 'tissue']/../*[key eq 'value' && value eq 'muscle']",
  attribute_value_match => {tissue => ['muscle']}
); 
ok($condition->entity_passes($sample),"Match a Dpath condition and an attribute condition");




done_testing();
