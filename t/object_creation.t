#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

my $data_dir = "$Bin/data";

use Bio::Metadata::Entity;
use Bio::Metadata::Attribute;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Validate::ValidationOutcome;

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
  links => [],
);

my $actural_sh  = $sample->to_hash();
my $expected_sh = {
  id          => 'bob',
  entity_type => 'sample',
  attributes  => [
    {
      name       => 'sex',
      value      => 'female',
      units      => undef,
      uri        => undef,
      id         => undef,
      source_ref => undef,
    },
    {
      name       => 'weight',
      value      => '0.05',
      units      => 'kg',
      uri        => undef,
      id         => undef,
      source_ref => undef,
    },
    {
      name       => 'tissue',
      value      => 'muscle',
      units      => undef,
      uri        => 'http://purl.obolibrary.org/obo/UBERON_0002385',
      id         => undef,
      source_ref => undef,
    },
    {
      name       => 'weight',
      value      => '50',
      units      => 'g',
      uri        => undef,
      id         => undef,
      source_ref => undef,
    },
  ],
  links => []

};
is_deeply( $actural_sh, $expected_sh, 'Entity to hash' );

is_deeply( $sample->attr_names, [qw(sex weight tissue)],
  'attr_names reports unique names in order' );

my $actual_organised_attrs  = $sample->organised_attr();
my $expected_organised_attr = {
  sex => [ Bio::Metadata::Attribute->new( name => 'sex', value => 'female' ), ],
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

my $rule_set = Bio::Metadata::Rules::RuleSet->new(
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

my $actual_rule_set_h     = $rule_set->to_hash();
my $expected_rule_group_h = {
  name        => 'g1',
  description => 'std',
  condition   => undef,
  rules       => [
    {
      name           => 'r1',
      type           => 'text',
      mandatory      => 'mandatory',
      allow_multiple => 0,
      condition      => undef
    },
    {
      name           => 'r2',
      type           => 'enum',
      mandatory      => 'mandatory',
      allow_multiple => 1,
      condition      => undef
    }
  ],
  imports => [],
};
my $expected_rule_set_h = {
  name        => 'ruleset_1',
  description => 'a test ruleset',
  rule_groups => [ $expected_rule_group_h, ],
};
is_deeply( $actual_rule_set_h, $expected_rule_set_h, 'Create ruleset' );

my $vo = Bio::Metadata::Validate::ValidationOutcome->new(
  rule_group => $rule_set->get_rule_group(0),
  rule       => $rule_set->get_rule_group(0)->get_native_rule(0),
  outcome    => 'error',
  entity     => $sample,
  attributes => [ $sample->get_attribute(0) ],
  message    => "c'est n'est pas un pipe",
);

my $actual_vo_h   = $vo->to_hash();
my $expected_vo_h = {
  rule_group_name => 'g1',
  rule            => {
    name           => 'r1',
    type           => 'text',
    mandatory      => 'mandatory',
    allow_multiple => 0,
    condition      => undef
  },
  message     => "c'est n'est pas un pipe",
  outcome     => 'error',
  entity_id   => 'bob',
  entity_type => 'sample',
  attributes  => [
    {
      name       => 'sex',
      value      => 'female',
      units      => undef,
      uri        => undef,
      id         => undef,
      source_ref => undef,
    },
  ],
};

is_deeply( $actual_vo_h, $expected_vo_h, 'Create validation outcome' );
done_testing();
