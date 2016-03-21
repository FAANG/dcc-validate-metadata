
=head1 LICENSE
   Copyright 2016 EMBL - European Bioinformatics Institute
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

package Bio::Metadata::Loader::RuleSetLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;

use JSON qw(decode_json);
use Try::Tiny;
use autodie;
use Data::Dumper;
use MooseX::Params::Validate;
use Bio::Metadata::Types;
use Bio::Metadata::Validate::Support::OlsLookup;

use Unicode::CaseFold;

has 'ols_lookup' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
  default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

requires 'load';

around 'load' => sub {
  my $orig = shift @_;
  my $self = shift @_;
  my @args = @_;

  my $rule_set   = $self->$orig(@args);
  my $ols_lookup = $self->ols_lookup;

  for my $g ( $rule_set->all_rule_groups ) {

    #import extra rules
    for my $i ( $g->all_imports ) {
      my $organised_rules = $g->organised_rules;

      #import, unless rule with same name already known in the group
      my $terms = $ols_lookup->matching_terms( $i->term );

      my @created_rules = map { $i->create_rule($_) } @$terms;
      my @rules_to_add =
        grep { !exists $organised_rules->{ fc $_->name } } @created_rules;
      my @elided_rules =
        grep { exists $organised_rules->{ fc $_->name } } @created_rules;

      $g->add_imported_rule(@rules_to_add);

      my $num_rules_added  = scalar(@rules_to_add);
      my $num_rules_elided = scalar(@elided_rules);
    }
  }

  return $rule_set;
};

1;
