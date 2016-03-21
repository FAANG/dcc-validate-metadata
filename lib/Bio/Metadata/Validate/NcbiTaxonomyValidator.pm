
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

package Bio::Metadata::Validate::NcbiTaxonomyValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;

use Scalar::Util qw(looks_like_number);
use Bio::Metadata::Attribute;

extends 'Bio::Metadata::Validate::OntologyIdAttributeValidator';

sub validate_attribute {
  my ( $self, $rule, $attribute) = @_;

  my $old_id = $attribute->id;

  if ($attribute->id && looks_like_number($attribute->id)){
    $attribute->id( 'NCBITaxon_'.$attribute->id);

  }
  my @ret = $self->SUPER::validate_attribute($rule, $attribute);

  $attribute->id($old_id);

  return @ret;
}
