#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Attribute;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::TextAttributeValidator;
use Bio::Metadata::Validate::NumberAttributeValidator;
use Bio::Metadata::Validate::EnumAttributeValidator;
use Bio::Metadata::Validate::UnitAttributeValidator;
use Bio::Metadata::Validate::RequirementValidator;
use Bio::Metadata::Validate::OntologyUriAttributeValidator;
use Bio::Metadata::Validate::OntologyTextAttributeValidator;;

my $text_attr = Bio::Metadata::Attribute->new( value => 'text', );
my $num_attr = Bio::Metadata::Attribute->new( value => 10, units => 'kg' );

my %base_outcome_h = (
    rule_group_name => undef,
    entity_id       => undef,
    entity_type     => undef,
    rule            => undef,
    attributes      => [],
);

text_rules();
num_rules();
enum_rules();
unit_rules();
mandatory_rules();
ontology_uri_rule();
ontology_text_rule();
done_testing();

sub text_rules {
    my $text_rule = Bio::Metadata::Rules::Rule->new( type => 'text', );
    my $text_attr_validator =
      Bio::Metadata::Validate::TextAttributeValidator->new();

    my %expected_t_outcome = (
        %base_outcome_h,
        message    => undef,
        outcome    => 'pass',
        rule       => $text_rule->to_hash,
        attributes => [ $text_attr->to_hash ]
    );

    my $t_outcome =
      $text_attr_validator->validate_attribute( $text_rule, $text_attr );

    is_deeply( $t_outcome->to_hash, \%expected_t_outcome,
        "text rule passes any content" );

}

sub num_rules {
    my $num_rule = Bio::Metadata::Rules::Rule->new( type => 'number' );
    my $num_attr_validator =
      Bio::Metadata::Validate::NumberAttributeValidator->new();

    my %expected_n_outcome = (
        %base_outcome_h,
        message    => undef,
        outcome    => 'pass',
        rule       => $num_rule->to_hash,
        attributes => [ $num_attr->to_hash ]
    );

    my $n_outcome =
      $num_attr_validator->validate_attribute( $num_rule, $num_attr );

    is_deeply( $n_outcome->to_hash, \%expected_n_outcome,
        "number rule passes integer" );

    my %expected_t_outcome = (
        %base_outcome_h,
        message    => 'value is not a number',
        outcome    => 'error',
        rule       => $num_rule->to_hash,
        attributes => [ $text_attr->to_hash ]
    );

    my $t_outcome =
      $num_attr_validator->validate_attribute( $num_rule, $text_attr );
    is_deeply( $t_outcome->to_hash, \%expected_t_outcome,
        "number rule rejects text" );
}

sub enum_rules {
    my $enum_rule = Bio::Metadata::Rules::Rule->new(
        type         => 'enum',
        valid_values => [ 'text', 'horse' ]
    );
    my $enum_attr_validator =
      Bio::Metadata::Validate::EnumAttributeValidator->new();

    my %expected_t_outcome = (
        %base_outcome_h,
        message    => undef,
        outcome    => 'pass',
        rule       => $enum_rule->to_hash,
        attributes => [ $text_attr->to_hash ]
    );

    my $t_outcome =
      $enum_attr_validator->validate_attribute( $enum_rule, $text_attr );

    is_deeply( $t_outcome->to_hash, \%expected_t_outcome,
        "enum rule passes expected value" );

    my %expected_n_outcome = (
        %base_outcome_h,
        message    => 'value is not in list of valid values:text,horse',
        outcome    => 'error',
        rule       => $enum_rule->to_hash,
        attributes => [ $num_attr->to_hash ]
    );

    my $n_outcome =
      $enum_attr_validator->validate_attribute( $enum_rule, $num_attr );
    is_deeply( $n_outcome->to_hash, \%expected_n_outcome,
        "enum rule rejects unexpected value" );
}

sub unit_rules {
    my $unit_rule = Bio::Metadata::Rules::Rule->new(
        type        => 'number',
        valid_units => ['kg']
    );
    my $unit_attr_validator =
      Bio::Metadata::Validate::UnitAttributeValidator->new();

    my %expected_n_outcome = (
        %base_outcome_h,
        message    => undef,
        outcome    => 'pass',
        rule       => $unit_rule->to_hash,
        attributes => [ $num_attr->to_hash ]
    );

    my $n_outcome =
      $unit_attr_validator->validate_attribute( $unit_rule, $num_attr );

    is_deeply( $n_outcome->to_hash, \%expected_n_outcome,
        "unit rule passes expected unit" );

    $unit_rule = Bio::Metadata::Rules::Rule->new(
        type        => 'number',
        valid_units => ['picoseconds']
    );

    my %expected_bn_outcome = (
        %base_outcome_h,
        message    => 'units are not in list of valid units:picoseconds',
        outcome    => 'error',
        rule       => $unit_rule->to_hash,
        attributes => [ $num_attr->to_hash ]
    );

    my $bn_outcome =
      $unit_attr_validator->validate_attribute( $unit_rule, $num_attr );
    is_deeply( $n_outcome->to_hash, \%expected_n_outcome,
        "unit rule rejects unexpected units" );

    my %expected_t_outcome = (
        %base_outcome_h,
        message    => 'no units provided, should be one of these:picoseconds',
        outcome    => 'error',
        rule       => $unit_rule->to_hash,
        attributes => [ $text_attr->to_hash ]
    );

    my $t_outcome =
      $unit_attr_validator->validate_attribute( $unit_rule, $text_attr );
    is_deeply( $t_outcome->to_hash, \%expected_t_outcome,
        "unit rule rejects absent units" );
}

sub ontology_uri_rule {
    my $ols_rule = Bio::Metadata::Rules::Rule->new(
        type => 'ontology_uri',
        valid_ancestor_uris =>
          ['http://purl.obolibrary.org/obo/UBERON_0002530'],
    );
    my $ols_text_attr_validator =
      Bio::Metadata::Validate::OntologyUriAttributeValidator->new();

    #valid term
    my $ols_attr = Bio::Metadata::Attribute->new(
        value => 'liver',
        uri   => 'http://purl.obolibrary.org/obo/UBERON_0002107'
    );
    my $outcome =
      $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'pass', 'OLS passed valid term' );

    #wrong ancestor
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'distal tarsal bone 4',
        uri   => 'http://purl.obolibrary.org/obo/UBERON_0010737'
    );
    $outcome = $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'error', 'OLS errored term with wrong ancestor' );

    #not a term URI
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'not a term',
        uri   => 'http://www.bbc.co.uk/cbeebies'
    );
    $outcome = $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'error', 'OLS errored URI term that is not in OLS' );

    #not URI
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'not a term',
        uri   => 'not a term'
    );
    $outcome = $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'error', 'OLS errored for term that is not a URI' );

    #warn for term/label mismatch
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'not a liver',
        uri   => 'http://purl.obolibrary.org/obo/UBERON_0002107'
    );
    $outcome =
      $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'warning',
        'OLS warning for term with different label/value term' );

}

sub ontology_text_rule {
    my $ols_rule = Bio::Metadata::Rules::Rule->new(
        type => 'ontology_text',
        valid_ancestor_uris =>
          ['http://purl.obolibrary.org/obo/UBERON_0002530'],
    );
    my $ols_text_attr_validator =
      Bio::Metadata::Validate::OntologyTextAttributeValidator->new();

      use Data::Dumper;


    #valid term
    my $ols_attr = Bio::Metadata::Attribute->new(
        value => 'liver'
    );
    my $outcome =
      $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );

    is( $outcome->outcome, 'pass', 'OLS passed valid term' );

    #wrong ancestor
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'distal tarsal bone 4'
    );
    $outcome = $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'error', 'OLS errored term with wrong ancestor' );

    #not a term
    $ols_attr = Bio::Metadata::Attribute->new(
        value => 'not a term'
    );
    $outcome = $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
    is( $outcome->outcome, 'error', 'OLS errored term that is not in OLS' );

}

sub mandatory_rules {
    my $validator = Bio::Metadata::Validate::RequirementValidator->new();

    my $mandatory_rule =
      Bio::Metadata::Rules::Rule->new( mandatory => 'mandatory' );
    my $recommended_rule =
      Bio::Metadata::Rules::Rule->new( mandatory => 'recommended' );
    my $optional_rule =
      Bio::Metadata::Rules::Rule->new( mandatory => 'optional' );

    my $mandatory_multiple_rule = Bio::Metadata::Rules::Rule->new(
        mandatory      => 'mandatory',
        allow_multiple => 1
    );

    my $no_attr   = [];
    my $one_attr  = [$text_attr];
    my $many_attr = [ $text_attr, $text_attr ];

    my %expected_error_outcome = (
        %base_outcome_h,
        message => 'mandatory attribute not present',
        outcome => 'error',
    );
    my %expected_multiple_error_outcome = (
        %base_outcome_h,
        message => 'multiple entries for attribute present',
        outcome => 'error',
    );
    my %expected_warning_outcome = (
        %base_outcome_h,
        message => 'recommended attribute not present',
        outcome => 'warning',
    );
    my %expected_pass_outcome = (
        %base_outcome_h,
        message => undef,
        outcome => 'pass',
    );

    #mandatory rule
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $mandatory_rule, $no_attr )
        ),
        \%expected_error_outcome,
        'mand attr absent - fail'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $mandatory_rule, $one_attr )
        ),
        \%expected_pass_outcome,
        'mand attr present - pass'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $mandatory_rule, $many_attr )

        ),
        \%expected_multiple_error_outcome,
        'mand attr present multiple - fail'
    );

    # recommended rule
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $recommended_rule, $no_attr )
        ),
        \%expected_warning_outcome,
        'recc attr absent - warn'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $recommended_rule, $one_attr )
        ),
        \%expected_pass_outcome,
        'recc attr present - pass'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $recommended_rule, $many_attr )
        ),
        \%expected_multiple_error_outcome,
        'recc attr present multiple - fail'
    );

    # optional rule
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $optional_rule, $no_attr )
        ),
        \%expected_pass_outcome,
        'opt attr absent - pass'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $optional_rule, $one_attr )
        ),
        \%expected_pass_outcome,
        'opt attr present - pass'
    );
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements( $optional_rule, $many_attr )
        ),
        \%expected_multiple_error_outcome,
        'opt attr present multiple - fail'
    );

    #mandatory multiple
    is_deeply(
        scrub_rule_attr(
            $validator->validate_requirements(
                $mandatory_multiple_rule, $many_attr
            )
        ),
        \%expected_pass_outcome,
        'multiple attr present - pass'
    );

}

sub scrub_rule_attr {
    my ($o) = @_;
    my $oh = $o->to_hash;
    $oh->{rule}       = undef;
    $oh->{attributes} = [];

    return $oh;
}
