# Copyright 2016 European Molecular Biology Laboratory - European Bioinformatics Institute
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
package Bio::Metadata::Rules::RuleImport;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use Bio::Metadata::Rules::PermittedTerm;

has 'rule_prefix' => ( is => 'ro', isa => 'Str' );
has 'term' => (
  is       => 'ro',
  isa      => 'Bio::Metadata::Rules::PermittedTerm',
  coerce   => 1,
  required => 1
);

sub create_rule {
  my ($self,$term) = @_;

  my $name = $self->rule_prefix ? $self->rule_prefix.$term->{label} : $term->{label} ;
  
  my $valid_term = Bio::Metadata::Rules::PermittedTerm->new(
    ontology_name => $self->term->ontology_name,
    term_iri => $term->{iri},
    allow_descendants => 0,
    include_root => 1,
  );

  return Bio::Metadata::Rules::Rule->new(
    name => $name,
    type => 'text',
    mandatory => 'optional',
    valid_terms => [$valid_term],
  );
}


sub to_hash {
  my ($self) = @_;
  return {
    rule_prefix => $self->rule_prefix,
    term        => $self->term->to_hash,
  };
}

__PACKAGE__->meta->make_immutable;
1;
