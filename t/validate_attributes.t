#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;
use Test::Exception;
use Text::Unidecode;

use Bio::Metadata::Attribute;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::TextAttributeValidator;
use Bio::Metadata::Validate::NumberAttributeValidator;
use Bio::Metadata::Validate::EnumAttributeValidator;
use Bio::Metadata::Validate::UnitAttributeValidator;
use Bio::Metadata::Validate::RequirementValidator;
use Bio::Metadata::Validate::OntologyUriAttributeValidator;
use Bio::Metadata::Validate::OntologyTextAttributeValidator;
use Bio::Metadata::Validate::OntologyIdAttributeValidator;
use Bio::Metadata::Validate::UriValueAttributeValidator;
use Bio::Metadata::Validate::DateAttributeValidator;
use Bio::Metadata::Validate::RelationshipValidator;

my $text_attr = Bio::Metadata::Attribute->new( value => 'text', );
my $num_attr = Bio::Metadata::Attribute->new( value => 10, units => 'kg' );

my %base_outcome_h = (
  rule_group_name => undef,
  entity_id       => undef,
  entity_type     => undef,
  rule            => undef,
  attributes      => [],
);

relationship_rules();
date_rules();
uri_rules();
text_rules();
num_rules();
date_rules();
enum_rules();
unit_rules();
mandatory_rules();
ontology_uri_rule();
ontology_id_rule();
ontology_text_rule();
done_testing();

sub relationship_rules {
  my $rel_rule = Bio::Metadata::Rules::Rule->new( type => 'relationship', );
  my $rel_validator = Bio::Metadata::Validate::RelationshipValidator->new();
  my ( $attr, $o );

  $attr = Bio::Metadata::Attribute->new( value => 'bob', );

  $o = $rel_validator->validate_attribute( $rel_rule, $attr );
  is( $o->outcome, 'error', 'no entities known' );

  $rel_validator->entities_by_id(
    { bob => Bio::Metadata::Entity->new( id => 'bob' ) } );
  $o = $rel_validator->validate_attribute( $rel_rule, $attr );
  is( $o->outcome, 'pass', 'entity known' );

  $attr = Bio::Metadata::Attribute->new( value => 'SAMEA676028', );
  $o = $rel_validator->validate_attribute( $rel_rule, $attr );
  is( $o->outcome, 'pass', 'biosamples entity known' );
}

sub date_rules {
  my $date_rule = Bio::Metadata::Rules::Rule->new( type => 'date', );
  my $date_attr_validator =
    Bio::Metadata::Validate::DateAttributeValidator->new();

  my ( $attr, $o );

  $attr = Bio::Metadata::Attribute->new(
    value => '2016-02-01',
    units => 'YYYY-MM-DD'
  );

  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "pass", "valid date passed" );

  $attr->value('2016-01-32');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "error", "subtly invalid date failed" );

  $attr->value('this is not a date');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "error", "very invalid date failed" );

  $attr->value('2016-02-29');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "pass", "Feb 29 passes for leap year" );

  $attr->value('2015-02-29');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "error", "Feb 29 fails for non-leap year" );

  $attr->units('MM-DD-YYYY');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "error",
    "unacceptable date format in attributes is rejected" );

  $attr->value('2016-02');
  $attr->units('YYYY-MM');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "pass", "valid month passed" );

  $attr->value('2016-31');
  $attr->units('YYYY-MM');
  $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
  is( $o->outcome, "error", "invalid month failed" );

  $date_rule->valid_units( ['MM-DD-YYYY'] );
  throws_ok(
    sub {
      $o = $date_attr_validator->validate_attribute( $date_rule, $attr );
    },
    qr/Rule has units that aren't a supported date format/,
    "Invalid format in rule dies with croak"
  );
}

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

sub ontology_id_rule {
  my $ols_rule = Bio::Metadata::Rules::Rule->new(
    type        => 'ontology_id',
    valid_terms => {
      term_iri      => 'http://purl.obolibrary.org/obo/UBERON_0002530',
      ontology_name => 'UBERON'
    },
  );
  my $ols_id_attr_validator =
    Bio::Metadata::Validate::OntologyIdAttributeValidator->new();
  my ( $ols_attr, $outcome );

  #valid term
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'liver',
    id    => 'UBERON_0002107'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'pass', 'OLS passed valid term - _ separator' );

  #valid term
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'liver',
    id    => 'UBERON:0002107'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'pass', 'OLS passed valid term - : separator' );

  #wrong ancestor
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'distal tarsal bone 4',
    id    => 'UBERON_0010737'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored term with wrong ancestor' );

  #not a term ID
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'not a term',
    id    => 'cbeebies'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored URI term that is not in OLS' );

  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored for term that is not a URI' );

  #warn for term/label mismatch
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'not a liver',
    id    => 'UBERON:0002107'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'warning',
    'OLS warning for term with different label/value term' );

  #pass for term/label check with unicode chars
  my $lbo_rule = Bio::Metadata::Rules::Rule->new(
    type        => 'ontology_id',
    valid_terms => {
      term_iri      => 'http://purl.obolibrary.org/obo/LBO_0000000',
      ontology_name => 'LBO'
    },
  );

  my $lbo_attr = Bio::Metadata::Attribute->new(
    value => 'Moxoto',
    id    => 'LBO_0001002 '
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $lbo_rule, $lbo_attr );
  is( $outcome->outcome, 'pass',
    'Pass for terms with unicode chars at OLS' );
  
  my ( $ols_attr_specimen);
  my $ols_rule_specimen = Bio::Metadata::Rules::Rule->new(
    type        => 'ontology_id',
    valid_terms => {
      term_iri      => 'http://purl.obolibrary.org/obo/OBI_0001479',
      ontology_name => 'OBI'
    },
  );

  #pass for specimen from organism
  $ols_attr_specimen = Bio::Metadata::Attribute->new(
    value => 'specimen from organism',
    id    => 'OBI_0001479'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule_specimen, $ols_attr_specimen );
  is( $outcome->outcome, 'pass', 'OLS passed for valid material' );
  
  #fail for not specimen from organism for
  $ols_attr_specimen = Bio::Metadata::Attribute->new(
    value => 'tissue specimen',
    id    => 'OBI_0001479'
  );
  $outcome = $ols_id_attr_validator->validate_attribute( $ols_rule_specimen, $ols_attr_specimen );
  is( $outcome->outcome, 'error', 'OLS failed for invalid material' );

}

sub uri_rules {
  my $uri_rule = Bio::Metadata::Rules::Rule->new( type => 'uri_value', );
  my $uri_value_validator =
    Bio::Metadata::Validate::UriValueAttributeValidator->new();

  my ( $attr, $outcome );

  #valid url
  $attr = Bio::Metadata::Attribute->new( value => 'https://www.ebi.ac.uk' );
  $outcome = $uri_value_validator->validate_attribute( $uri_rule, $attr );
  is( $outcome->outcome, 'pass', 'Valid url passed' );

  #valid mailto
  $attr = Bio::Metadata::Attribute->new( value => 'mailto:bob@example.org' );
  $outcome = $uri_value_validator->validate_attribute( $uri_rule, $attr );
  is( $outcome->outcome, 'pass', 'Valid mailto passed' );

  #vaild ftp
  $attr = Bio::Metadata::Attribute->new( value => 'ftp://ftp.ebi.ac.uk' );
  $outcome = $uri_value_validator->validate_attribute( $uri_rule, $attr );
  is( $outcome->outcome, 'pass', 'Valid ftp passed' );

  #not a uri
  $attr =
    Bio::Metadata::Attribute->new( value => 'not actually a URI in a way' );
  $outcome = $uri_value_validator->validate_attribute( $uri_rule, $attr );
  is( $outcome->outcome, 'error', 'Invalid url failed' );

  #unsupported uri type
  $attr =
    Bio::Metadata::Attribute->new(
    value => 'telnet://bob:password@example.org:9000' );
  $outcome = $uri_value_validator->validate_attribute( $uri_rule, $attr );
  is( $outcome->outcome, 'error', 'Unsupported schema failed' );
  is(
    $outcome->message,
'uri scheme is not supported. It is telnet but only http, https, ftp, mailto are accepted',
    'Unsupported schema failed with correct message'
  );
}

sub ontology_uri_rule {
  my $ols_rule = Bio::Metadata::Rules::Rule->new(
    type        => 'ontology_uri',
    valid_terms => [{
      term_iri      => 'http://purl.obolibrary.org/obo/PATO_0000047',
      ontology_name => 'PATO'
    }],
  );

  my $ols_text_attr_validator =
    Bio::Metadata::Validate::OntologyUriAttributeValidator->new();

  #valid term
  my $ols_attr = Bio::Metadata::Attribute->new(
    value => 'male genotypic sex',
    uri   => 'http://purl.obolibrary.org/obo/PATO_0020001'
  );
  my $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'pass', 'OLS passed valid term' );

  #wrong ancestor
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'unicellular',
    uri   => 'http://purl.obolibrary.org/obo/PATO_0001994'
  );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored term with wrong ancestor' );

  #not a term URI
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'not a term',
    uri   => 'http://www.bbc.co.uk/cbeebies'
  );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored URI term that is not in OLS' );

  #not URI
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'not a term',
    uri   => 'not a term'
  );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored for term that is not a URI' );

  #warn for term/label mismatch
  $ols_attr = Bio::Metadata::Attribute->new(
    value => 'male',
    uri   => 'http://purl.obolibrary.org/obo/PATO_0020001'
  );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'warning',
    'OLS warning for term with different label/value term' );

}

sub ontology_text_rule {
  my $ols_rule = Bio::Metadata::Rules::Rule->new(
    type        => 'ontology_text',
    valid_terms => {
      term_iri      => 'http://purl.obolibrary.org/obo/UBERON_0002530',
      ontology_name => 'UBERON'
    },
  );
  my $ols_text_attr_validator =
    Bio::Metadata::Validate::OntologyTextAttributeValidator->new();


  #valid term
  my $ols_attr = Bio::Metadata::Attribute->new( value => 'liver' );
  my $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );

  is( $outcome->outcome, 'pass', 'OLS passed valid term' );

  #wrong ancestor
  $ols_attr = Bio::Metadata::Attribute->new( value => 'distal tarsal bone 4' );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored term with wrong ancestor' );

  #not a term
  $ols_attr = Bio::Metadata::Attribute->new( value => 'not a term' );
  $outcome =
    $ols_text_attr_validator->validate_attribute( $ols_rule, $ols_attr );
  is( $outcome->outcome, 'error', 'OLS errored term that is not in OLS' );

}

sub mandatory_rules {
  my $validator = Bio::Metadata::Validate::RequirementValidator->new();

  my $mandatory_rule =
    Bio::Metadata::Rules::Rule->new( mandatory => 'mandatory', type => 'text' );
  my $recommended_rule = Bio::Metadata::Rules::Rule->new(
    mandatory => 'recommended',
    type      => 'text'
  );
  my $optional_rule =
    Bio::Metadata::Rules::Rule->new( mandatory => 'optional', type => 'text' );

  my $mandatory_multiple_rule = Bio::Metadata::Rules::Rule->new(
    mandatory      => 'mandatory',
    allow_multiple => 1,
    type           => 'text'
  );

  my $no_attr   = [];
  my $one_attr  = [$text_attr];
  my $many_attr = [ $text_attr, $text_attr ];

  my %expected_error_outcome = (
    %base_outcome_h,
    message => ':mandatory attribute not present',
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
      $validator->validate_requirements( $mandatory_multiple_rule, $many_attr )
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
