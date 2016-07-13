#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Attribute;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::OntologyIdAttributeValidator;

my $attr = Bio::Metadata::Attribute->new(
  value => 'allantoic fluid',
  id    => 'BTO_0001662'
);

my $rule = Bio::Metadata::Rules::Rule->new(
  type        => 'ontology_id',
  valid_terms => [
    {
      term_iri      => "http://purl.obolibrary.org/obo/BTO_0000042",
      ontology_name => "BTO"
    },
  ]
);

my $ols_id_attr_validator =
  Bio::Metadata::Validate::OntologyIdAttributeValidator->new();

my $outcome = $ols_id_attr_validator->validate_attribute( $rule, $attr );

is( $outcome->outcome, 'pass', 'OLS lookup traverses \'part of\' relations' );
done_testing();