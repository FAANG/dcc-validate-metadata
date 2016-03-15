# Copyright 2015 European Molecular Biology Laboratory - European Bioinformatics Institute
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
package Bio::Metadata::Rules::RuleGroup;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Rules::Condition;
use Bio::Metadata::Rules::RuleImport;

has 'name'        => ( is => 'rw', isa => 'Str', );
has 'description' => ( is => 'rw', isa => 'Str' );
has 'condition' =>
  ( is => 'rw', isa => 'Bio::Metadata::Rules::Condition', coerce => 1 );
has 'rules' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::Rules::RuleArrayRef',
  handles => {
    all_rules   => 'elements',
    add_rule    => 'push',
    count_rules => 'count',
    get_rule    => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);
has 'imports' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::Rules::RuleImportArrayRef',
  handles => {
    all_imports   => 'elements',
    add_imports   => 'push',
    count_imports => 'count',
    get_imports   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

sub to_hash {
  my ($self) = @_;

  my @r = map { $_->to_hash } $self->all_rules;
  my @i = map { $_->to_hash } $self->all_imports;

  return {
    name        => $self->name,
    description => $self->description,
    condition   => $self->condition,
    rules       => \@r,
    imports     => \@i,
  };
}

__PACKAGE__->meta->make_immutable;

1;
