
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

package Bio::Metadata::Faang::FaangChildOfCyclicCheck;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Types;
use List::MoreUtils qw(uniq);

use Bio::Metadata::Validate::Support::BioSDLookup;
use Bio::Metadata::Rules::PermittedTerm;

has description => (
  is  => 'rw',
  isa => 'Str',
  default =>
'Ensure that the parent is not listing the child as its parent.',
);

has name => (
  is      => 'rw',
  isa     => 'Str',
  default => 'Child/parents ID',
);

#must consume after declaring attribute that satisfies requirement for 'description'
with 'Bio::Metadata::Consistency::ConsistencyCheckRole';

has 'biosd_lookup' => (
  is       => 'rw',
  isa      => 'Bio::Metadata::Validate::Support::BioSDLookup',
  required => 1,
  default  => sub { Bio::Metadata::Validate::Support::BioSDLookup->new() },
);

sub check_entity {
  my ( $self, $entity, $entities_by_id ) = @_;
  my @outcomes;

  my $organised_attr      = $entity->organised_attr;
  my $child_id            = $organised_attr->{'Sample Name'}->[0]->{'value'};
  my $parents_ids         = $organised_attr->{'child of'};

  unless ( $parents_ids
    && scalar(@$parents_ids) > 0 )
  {
    #not enough information for higher level checks
    return \@outcomes;
  }

  my @parents_child_of;

  foreach my $sample_identifier ( @{$parents_ids} ) {
    my $parent_entity;

    if ( $entities_by_id->{ $sample_identifier->{'value'} }
      && $sample_identifier->allow_further_validation )
    {
      $parent_entity = $entities_by_id->{ $sample_identifier->{'value'} };
    }

    if ( !defined $parent_entity ) {
      $parent_entity =
        $self->biosd_lookup->fetch_sample( $sample_identifier->{'value'} );
    }

    if ( defined $parent_entity ) {
      my $parent_organised_attr = $parent_entity->organised_attr;
      my $parent_species_attrs  = $parent_organised_attr->{'child of'};

      push( @parents_child_of,    $parent_species_attrs->[0]->{'value'} );
    }
  }



  my $outcome =
    Bio::Metadata::Validate::ValidationOutcome->new(
    attributes => $parents_ids, );
  push @outcomes, $outcome;

  my %parents_parents = map { $_ => 1 } @parents_child_of;

  #Test if more than one species i.e. child and parent mismatch
  if ( exists($parents_parents{$child_id} )) {
    $outcome->outcome('error');
    $outcome->message(
    "The parent of child ($child_id) lists this child as its own parent: "
        . join( ', ', @parents_child_of ) );
  }
  else {
    $outcome->outcome('pass');
  }

  return \@outcomes;
}

__PACKAGE__->meta->make_immutable;

1;
