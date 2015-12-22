#!/usr/bin/env perl

use strict;
use warnings;

use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Attribute;
use Bio::Metadata::Validate::OntologyUriAttributeValidator;
use Bio::Metadata::Validate::EnumAttributeValidator;

#valid
my $valid_ols_attr = Bio::Metadata::Attribute->new(
	value	=> 'myeloid cell', 
	uri => 'http://purl.obolibrary.org/obo/CL_0000763'
	);
	
my $bad_ols_attr = Bio::Metadata::Attribute->new(
	value	=> 'common lymphoid progenitor', 
	uri => 'http://purl.obolibrary.org/obo/CL_0000052'
	);

my $ols_rule = Bio::Metadata::Rules::Rule->new(
	type => 'ontology_uri',
	valid_ancestor_uris =>
		['http://purl.obolibrary.org/obo/CL_0000003']
);
	
my $enum_rule = Bio::Metadata::Rules::Rule->new(
    type         => 'enum',
    valid_values => [ 'http://purl.obolibrary.org/obo/CL_0000763', 'http://purl.obolibrary.org/obo/CL_0000809' ]
);
	
my $ols_attr_validator = Bio::Metadata::Validate::OntologyUriAttributeValidator->new();

my $outcome1 = $ols_attr_validator->validate_attribute( $ols_rule, $valid_ols_attr );

print $outcome1->outcome,"\n";
print $outcome1->message,"\n";

my $enum_attr_validator = Bio::Metadata::Validate::EnumAttributeValidator->new();

my $outcome2 = $enum_attr_validator->validate_attribute( $enum_rule, $bad_ols_attr );

print $outcome2->outcome,"\n";
print $outcome2->message,"\n";

my $outcome3 = $ols_attr_validator->validate_attribute( $ols_rule, $bad_ols_attr );

print $outcome3->outcome,"\n";
print $outcome3->message,"\n";

print "hello\n";