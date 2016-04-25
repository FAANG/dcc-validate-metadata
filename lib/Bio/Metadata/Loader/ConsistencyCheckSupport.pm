
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

package Bio::Metadata::Loader::ConsistencyCheckSupport;

use strict;
use warnings;

use Carp;
use Moose;
use MooseX::Params::Validate;

has 'consistency_check_lookup' => (
  is      => 'rw',
  isa     => 'HashRef[Bio::Metadata::Consistency::ConsistencyCheckRole]',
  default => sub {
    return {

    };
  },
  handles => { get_consistency_check_instance => 'get', },
);

sub load_consistecy_checks {
  my ( $self, $rule_set ) = @_;

  for my $rg ( $rule_set->all_rule_groups ) {
    for my $pair ( $rg->consistency_check_pairs ) {
      my $name = $pair->[0];
      my $config = $pair->[1] || {};

      my $example_obj = $self->get_consistency_check_instance($name);
      die "No consistency check found for name" if (!$example_obj);

      my $check_instance = (blessed $example_obj)->new($config);
      $rg->set_consistency_check($name,$check_instance);
    }
  }
}

1;
