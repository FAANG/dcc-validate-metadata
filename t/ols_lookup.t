#!/usr/bin/env perl

use strict;
use warnings;
use Test::More;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";
use Data::Dumper;
use Test::More;

use Bio::Metadata::Validate::Support::OlsLookup;
use Bio::Metadata::Rules::PermittedTerm;

my $ols_lookup = Bio::Metadata::Validate::Support::OlsLookup->new();

test_few_descendents();
test_many_descendents();

test_ancestor_uri_pass();
test_ancestor_uri_fail();

test_all_children_ancestor_uri_pass();
test_all_children_ancestor_uri_fail();

test_all_children_childof_fail();
test_all_children_childof_pass_pato();
test_all_children_childof_pass_uberon();

done_testing();

sub test_many_descendents {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'ERO',
    term_iri          => 'http://purl.obolibrary.org/obo/BFO_0000002',
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 1
  );

  my $terms                    = $ols_lookup->matching_terms( $pt );
  my $expected_number_of_terms = 3149;

  is( scalar(@$terms), $expected_number_of_terms,
    'Loaded continuant terms from ERO' );

  my $number_without_iri        = 0;
  my $number_without_label      = 0;
  my $number_without_short_form = 0;

  for my $term (@$terms) {
    $number_without_iri++        unless $term->{iri};
    $number_without_label++      unless $term->{label};
    $number_without_short_form++ unless $term->{short_form};
  }

  is( $number_without_iri,        0, 'All terms should have an IRI' );
  is( $number_without_label,      0, 'All terms should have a label' );
  is( $number_without_short_form, 0, 'All terms should have a short form' );
}

sub test_few_descendents {

  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'ERO',
    term_iri          => 'http://purl.org/net/OCRe/study_design.owl#OCRE100038',
    allow_descendants => 1,
    leaf_only         => 1,
    include_root      => 0,
  );

  my $terms          = $ols_lookup->matching_terms( $pt );
  my $reduced_terms  = $ols_lookup->_reduce_terms($terms);
  my $expected_terms = [
    {
      label      => 'Phase 1',
      obo_id     => 'Phase:1',
      short_form => 'Phase_1',
      iri        => 'http://purl.org/net/OCRe/study_design.owl#Phase_1'
    },
    {
      label      => 'Phase 2',
      obo_id     => 'Phase:2',
      short_form => 'Phase_2',
      iri        => 'http://purl.org/net/OCRe/study_design.owl#Phase_2'
    },
    {
      label      => 'Phase 3',
      obo_id     => 'Phase:3',
      short_form => 'Phase_3',
      iri        => 'http://purl.org/net/OCRe/study_design.owl#Phase_3'
    },
    {
      label      => 'Phase 4',
      obo_id     => 'Phase:4',
      short_form => 'Phase_4',
      iri        => 'http://purl.org/net/OCRe/study_design.owl#Phase_4'
    },
    {
      label      => 'Phase 0',
      obo_id     => 'Phase:0',
      short_form => 'Phase_0',
      iri        => 'http://purl.org/net/OCRe/study_design.owl#Phase_0'
    },
  ];
  is_deeply( $reduced_terms, $expected_terms,
    'Loaded Phase terms from ERO (small scale, details right)' );

}

sub test_ancestor_uri_pass {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'UBERON',
    term_iri          => 'http://purl.obolibrary.org/obo/UBERON_0002530',
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $ancestor_uri   = 'http://purl.obolibrary.org/obo/UBERON_0002530'; # tissue
  my $pass_uri       = 'http://purl.obolibrary.org/obo/UBERON_0002107'; # liver'
  my $expected_label = 'liver';

  my $output = $ols_lookup->find_match( $pass_uri, $pt );
  is( $output->{label}, $expected_label, "Get match for liver under good uri for find_match" );
}

sub test_ancestor_uri_fail {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'UBERON',
    term_iri          => 'http://purl.obolibrary.org/obo/UBERON_0002530',
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $fail_uri       = 'http://www.bbc.co.uk/cbeebies';    # not an ontology uri
  my $expected_label = '';

  my $output = $ols_lookup->find_match( $fail_uri, $pt );
  is( $output, $expected_label, "Get undef for liver under bogus uri for find_match" );
}

sub test_all_children_childof_fail {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'PATO',
    term_iri          => 'http://purl.obolibrary.org/obo/PATO_0000047', #Biological sex
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $pass_uri       = 'http://purl.obolibrary.org/obo/PATO_0001994'; # unicellular
  my $expected_label = '';

  my $output = $ols_lookup->_find_match_all_children( $pass_uri, $pt );
  is( $output, $expected_label, "Expect empty string for query that is not child of permitted term _find_match_all_children" );
}

sub test_all_children_childof_pass_pato {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'PATO',
    term_iri          => 'http://purl.obolibrary.org/obo/PATO_0000047', #Biological sex
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $pass_uri       = 'http://purl.obolibrary.org/obo/PATO_0020001'; # male genotypic sex
  my $expected_label = 'male genotypic sex';

  my $output = $ols_lookup->_find_match_all_children( $pass_uri, $pt );
  is( $output->{label}, $expected_label, "Get valid match for child of permitted term in PATO ontology _find_match_all_children" );
}

sub test_all_children_childof_pass_uberon {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'UBERON',
    term_iri          => 'http://purl.obolibrary.org/obo/UBERON_0002530', #gland
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $pass_uri       = 'http://purl.obolibrary.org/obo/UBERON_0002107'; # liver
  my $expected_label = 'liver';

  my $output = $ols_lookup->_find_match_all_children( $pass_uri, $pt );
  is( $output->{label}, $expected_label, "Get valid match for child of permitted term in UBERON ontology _find_match_all_children" );
}

sub test_all_children_ancestor_uri_pass {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'BTO',
    term_iri          => 'http://purl.obolibrary.org/obo/BTO_0000042',
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $ancestor_uri   = 'http://purl.obolibrary.org/obo/BTO_0000042'; # animal
  my $pass_uri       = 'http://purl.obolibrary.org/obo/BTO_0000045'; # adrenal cortex
  my $expected_label = 'adrenal cortex';

  my $output = $ols_lookup->_find_match_all_children( $pass_uri, $pt );
  is( $output->{label}, $expected_label, "Get valid match via part of relationships using find_match_all_children" );
}

sub test_all_children_ancestor_uri_fail {
  my $pt = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name     => 'BTO',
    term_iri          => 'http://purl.obolibrary.org/obo/UBERON_0002530',
    allow_descendants => 1,
    leaf_only         => 0,
    include_root      => 0,
  );

  my $fail_uri       = 'http://www.bbc.co.uk/cbeebies';    # not an ontology uri
  my $expected_label = '';

  my $output = $ols_lookup->find_match_all_children( $fail_uri, $pt );
  is( $output, $expected_label, "Get undef for liver under bogus uri for find_match_all_children" );
}