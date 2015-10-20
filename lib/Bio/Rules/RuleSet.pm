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
package Bio::Rules::RuleSet;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Validate::Types;
use Bio::Rules::RuleGroup;

has 'name'        => ( is => 'rw', isa => 'Str' );
has 'description' => ( is => 'rw', isa => 'Str' );
has 'rule_groups' => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'Bio::Rules::RuleGroupArrayRef',
    handles => {
        all_rule_groups   => 'elements',
        add_rule_group    => 'push',
        count_rule_groups => 'count',
        get_rule_group    => 'get',
    },
    default => sub { [] },
    coerce  => 1,
);

sub to_hash {
    my ($self) = @_;

    my @rg = map { $_->to_hash } $self->all_rule_groups;

    return {
        name        => $self->name,
        description => $self->description,
        rule_groups => \@rg,
    };
}
1;
