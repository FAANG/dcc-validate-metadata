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
package Bio::Metadata::Validate;
our $VERSION = '0.01';
1;
__END__
=pod

=head1 NAME

Bio::Metadata::Validate - a validation system for biological metadata

=head1 VERSION

version 0.01

=head1 SYNOPSIS



=head1 DESCRIPTION

Validate metadata aganist a schema and a checklist

=cut

use Bio::Metadata::Attribute;
use Bio::Metadata::Entity;

use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Rules::RuleGroup;
use Bio::Metadata::Rules::RuleSet;

use Bio::Metadata::Loader::RuleSetLoader;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Validate::EnumAttributeValidator;
use Bio::Metadata::Validate::NumberAttributeValidator;
use Bio::Metadata::Validate::RequirementValidator;
use Bio::Metadata::Validate::TextAttributeValidator;
use Bio::Metadata::Validate::UnitAttributeValidator;
use Bio::Metadata::Validate::ValidationOutcome;


1;
