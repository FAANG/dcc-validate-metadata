
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

package Bio::Metadata::Validate::AttributeValidatorRole;

use Moose::Role;
use MooseX::Params::Validate;
use Bio::Metadata::Validate::ValidationOutcome;

requires 'validate_attribute';

around 'validate_attribute' => sub {
  my $orig = shift;
  my $self = shift;
  my ( $rule, $attribute, $o ) = pos_validated_list(
    \@_,
    { isa => 'Bio::Metadata::Rules::Rule' },
    { isa => 'Bio::Metadata::Attribute' },
    { isa => 'Bio::Metadata::Validate::ValidationOutcome', optional => 1 },
  );

  if ( !$o ) {
    $o = Bio::Metadata::Validate::ValidationOutcome->new(
      attributes => [$attribute],
      rule       => $rule
    );
  }
  return $self->$orig( $rule, $attribute, $o );
};

1;
