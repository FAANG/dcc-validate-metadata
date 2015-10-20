
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

package Bio::Metadata::Validate::RequirementValidator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Metadata::Validate::ValidationOutcome;
use MooseX::Params::Validate;

sub validate_requirements {
  my ($self) = shift;
  my ( $rule, $attributes ) = pos_validated_list(
      \@_,
      { isa => 'Bio::Metadata::Rules::Rule' },
      { isa => 'Bio::Metadata::AttributeArrayRef' }
  );
  
  my $o = Bio::Metadata::Validate::ValidationOutcome->new();

  my $num_attrs =  scalar(@$attributes) ;

  if ($rule->mandatory eq 'mandatory' && $num_attrs == 0) {
    $o->outcome('error');
    $o->message('mandatory attribute not present');
  }
  elsif ($rule->mandatory eq 'recommended'  && $num_attrs == 0 ){
    $o->outcome('warning');
    $o->message('recommended attribute not present');
  }
  elsif (!$rule->allow_multiple && $num_attrs > 1){
    $o->outcome('error');
    $o->message('multiple entries for attribute present');
  }
  else {
    $o->outcome('pass');
  }
  
  return $o;
}

1;