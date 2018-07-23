
=head1 LICENSE
   Copyright 2015 EMBL - European Bioinformatics Institute
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
=cut

package Bio::Metadata::Validate::RequirementValidator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

my $not_applicable_term    = 'not applicable';
my $not_collected_term     = 'not collected';
my $not_provided_term      = 'not provided';
my $restricted_access_term = 'restricted access';

has 'missing_values_terms' => (
  is      => 'ro',
  isa     => 'ArrayRef[Str]',
  traits  => ['Array'],
  default => sub {
    [
      $not_applicable_term, $not_collected_term,
      $not_provided_term,   $restricted_access_term,
    ];
  },
  handles => {
    'all_missing_values_terms' => 'elements',
    'find_missing_values_term' => 'first',
  },
);

has 'missing_value_outcome' => (
  is      => 'ro',
  isa     => 'HashRef[HashRef[Str]]',
  default => sub {
    return {
      mandatory => {
        $not_applicable_term    => 'error',
        $not_collected_term     => 'error',
        $not_provided_term      => 'error',
        $restricted_access_term => 'warning',
      },
      recommended => {
        $not_applicable_term    => 'pass',
        $not_collected_term     => 'warning',
        $not_provided_term      => 'warning',
        $restricted_access_term => 'pass',
      },
      optional => {
        $not_applicable_term    => 'error',
        $not_collected_term     => 'error',
        $not_provided_term      => 'error',
        $restricted_access_term => 'error',
      },
    };
  },
);

sub validate_requirements {
  my ($self,$rule, $attributes) = @_;
  my $o = Bio::Metadata::Validate::ValidationOutcome->new(
    attributes => $attributes,
    rule       => $rule,
  );
  $self->validate_by_count( $o, $attributes, $rule );

  if ( !defined $o->outcome ) {
    $self->check_missing_values( $o, $attributes, $rule );
  }
  if ( !defined $o->outcome ) {
    $o->outcome('pass');
  }
  return $o;
}

sub check_missing_values {
  my ( $self, $outcome, $attributes, $rule ) = @_;

  for my $a (@$attributes) {
    if ( defined $a->value
      && $self->find_missing_values_term( sub { $a->value eq $_ } ) )
    {
      #this is a missing value, no further work to do
      $a->block_further_validation;

      my $outcome_type =
        $self->missing_value_outcome->{ $rule->mandatory }{ $a->value };

      $outcome->outcome($outcome_type);
      if ( $outcome_type ne 'pass' ) {
        if ( $rule->mandatory eq 'optional'){
          $outcome->message('This field is optional, so if not providing real data please leave the field blank');
        }elsif($a->name eq 'Derived from' and $a->value eq 'restricted access'){
          $outcome->message('This field cannot be restricted access and must be a valid BioSample');
          $outcome->outcome('error');
        }else{
          $outcome->message( 'attribute is ' . $rule->mandatory );
        }    
      }
    }
  }
}

sub validate_by_count {
  my ( $self, $o, $attributes, $rule ) = @_;
  my $num_attrs = scalar(@$attributes);
  my $rule_name = "";
  $rule_name = $rule->name if (exists $rule{name});

  if ( $rule->mandatory eq 'mandatory' && $num_attrs == 0 ) {
    $o->outcome('error');
    $o->message("${rule_name}:mandatory attribute not present");
  }
  elsif ( $rule->mandatory eq 'recommended' && $num_attrs == 0 ) {
    $o->outcome('warning');
    $o->message("${rule_name}:recommended attribute not present");
  }
  elsif ( !$rule->allow_multiple && $num_attrs > 1 ) {
    $o->outcome('error');
    $o->message("${rule_name}:multiple entries for attribute present");
  }
  if ( $o->message ) {
    my $new_message = $o->message . ' - ';
    if ($rule && defined $rule->name){
      $new_message .= $rule->name
    }
    elsif ($attributes->[0] && defined $attributes->[0]->name){
            $new_message .= $attributes->[0]->name;
    }
    $o->message( $o->message );
  }
}

__PACKAGE__->meta->make_immutable;
1;
