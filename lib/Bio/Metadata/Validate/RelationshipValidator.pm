
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

package Bio::Metadata::Validate::RelationshipValidator;

use strict;
use warnings;
use Bio::Metadata::Validate::Support::BioSDLookup;

use Moose;
use namespace::autoclean;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'entities_by_id' => (
    traits  => ['Hash'],
    is      => 'rw',
    isa     => 'HashRef[Bio::Metadata::Entity]',
    handles => { get_entity_by_id => 'get' },
);

has 'biosd_lookup' => (
    is  => 'rw',
    isa => 'Bio::Metadata::Validate::Support::BioSDLookup',
    required => 1,
    default => sub {Bio::Metadata::Validate::Support::BioSDLookup->new()},
);

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    my $sample_identifier = $attribute->value;
    my $entity            = $self->get_entity_by_id($sample_identifier);

    if ( !defined $entity) {
      $entity = $self->biosd_lookup->fetch_sample($sample_identifier);
    }

    if ( !defined $entity ) {
        $o->outcome('error');
        $o->message('No entity found');
        return $o;
    }

    foreach my $attr(@{$entity->attributes}){
      my $value = $attr->value;
      if($attr->name eq "material"){
        $attr->name("Material");
        last;
      }
    }

    if ( $rule->condition && !$rule->condition->entity_passes($entity) ) {
        $o->outcome('error');
        $o->message('referenced entity does not match condition');
        return $o;
    }

    $o->outcome('pass');

    return $o;
}
__PACKAGE__->meta->make_immutable;
1;
