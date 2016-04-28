
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

package Bio::Metadata::Reporter::ReporterRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use MooseX::Params::Validate;
use Bio::Metadata::Reporter::AttributeColumn;
use Bio::Metadata::Entity;

requires 'report';

has 'file_path'    => ( is => 'rw', isa => 'Str' );
has 'file_handle'  => ( is => 'rw', isa => 'FileHandle' );

before 'report' => sub {
  my $self = shift;
  my ( $entities, $entity_status, $entity_outcomes ) = validated_list(
    \@_,
    entities      => { isa => 'Bio::Metadata::EntityArrayRef' },
    entity_status => { isa => 'HashRef[Bio::Metadata::Validate::OutcomeEnum]' },
    entity_outcomes =>
      { isa => 'HashRef[Bio::Metadata::Validate::ValidationOutcomeArrayRef]' },
    attribute_status =>
      { isa => 'HashRef[Bio::Metadata::Validate::OutcomeEnum]' },
    attribute_outcomes =>
      { isa => 'HashRef[Bio::Metadata::Validate::ValidationOutcomeArrayRef]' },
    rule_set => { isa => 'Bio::Metadata::Rules::RuleSet',optional => 1},
  );
};

sub determine_attr_columns {
  my ( $self, $entities, $rule_set ) = @_;

  my @columns;
  my %column;
  my $entity = Bio::Metadata::Entity->new();
  if ($rule_set) {
    for my $rg ( $rule_set->all_rule_groups ) {
      for my $r ( $rg->all_rules ) {
        my $name = $entity->normalise_attribute_name($r->name);
        if ( !$column{$name} ) {
          $column{$name} =
            Bio::Metadata::Reporter::AttributeColumn->new( name => $name );
          push @columns, $column{$name};
        }
      }
    }
  }

  for my $e (@$entities) {
    my $organised_attr = $e->organised_attr;

    for my $name ( @{ $e->attr_names } ) {

      my $attrs = $organised_attr->{$name} // [];

      if ( !$column{$name} ) {
        $column{$name} =
          Bio::Metadata::Reporter::AttributeColumn->new( name => $name );
        push @columns, $column{$name};
      }

      my $ac = $column{$name};
      $ac->consume_attrs($attrs);
    }
  }

  return \@columns;
}

1;
