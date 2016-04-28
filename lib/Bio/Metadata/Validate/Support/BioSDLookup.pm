
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

package Bio::Metadata::Validate::Support::BioSDLookup;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;

use BioSD;
use BioSD::Session;
use Bio::Metadata::Entity;

has 'biosd_session' => (
  is       => 'rw',
  isa      => 'BioSD::Session',
  required => 1,
  default  => sub { BioSD::Session->new() }
);

sub fetch_sample {
  my ( $self, $id ) = @_;

  my $sample = $self->biosd_session->fetch_sample($id);
  return undef if ( !$sample || !$sample->is_valid );

  return $self->convert_biosample_to_entity($sample);
}

sub fetch_group_samples {
  my ( $self, $id ) = @_;

  my $group = $self->biosd_session->fetch_group($id);
  return undef if ( !$group || !$group->id || !$group->is_valid );

  my @group_samples =
    map { $self->convert_biosample_to_entity($_) } @{ $group->samples };

  return \@group_samples;
}

sub convert_biosample_to_entity {
  my ( $self, $sample ) = @_;

  my $entity = Bio::Metadata::Entity->new(
    id          => $sample->id,
    entity_type => 'sample',
    synonyms    => [ $sample->id ],
  );

  for my $property ( @{ $sample->properties } ) {
    for my $qualified_value ( @{ $property->qualified_values } ) {
      if ( $property->class eq 'Sample Name' ) {
        $entity->id( $qualified_value->value );
        next;
      }

      my $attribute = Bio::Metadata::Attribute->new(
        name  => $property->class,
        value => $qualified_value->value,
      );
      $attribute->units( $qualified_value->unit )
        if ( $qualified_value->unit );

      my $term_source = $qualified_value->term_source;
      if ($term_source) {
        $attribute->uri( $term_source->uri ) if defined $term_source->uri;
        $attribute->id( $term_source->term_source_id )
          if defined $term_source->term_source_id;
        $attribute->source_ref( $term_source->name )
          if defined $term_source->name;
      }

      $entity->add_attribute($attribute);
    }
  }

  for my $df ( @{ $sample->derived_from } ) {
    $entity->add_attribute(Bio::Metadata::Attribute->new(
      name  => 'Derived from',
      value => $df->id,
    ));
  }


  return $entity;
}

__PACKAGE__->meta->make_immutable;

1;
