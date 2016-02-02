
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

package Bio::Metadata::Types;

use strict;
use warnings;
use Carp;
use Moose::Util::TypeConstraints;

enum 'Bio::Metadata::Rules::Rule::TypeEnum',
  [qw(text number enum ontology_uri ontology_text ontology_id uri_value date)];
enum 'Bio::Metadata::Rules::Rule::MandatoryEnum',
  [qw(mandatory recommended optional)];

enum 'Bio::Metadata::Validate::OutcomeEnum', [qw(pass error warning)];

role_type 'Bio::Metadata::Validate::AttributeValidatorRole';
role_type 'Bio::Metadata::Loader::JSONLoaderRole';

#attribute
class_type 'Bio::Metadata::Attribute';

coerce 'Bio::Metadata::Attribute' => from 'HashRef' =>
  via { Bio::Metadata::Attribute->new($_); };

subtype 'Bio::Metadata::AttributeArrayRef' => as
  'ArrayRef[Bio::Metadata::Attribute]';

coerce 'Bio::Metadata::AttributeArrayRef' => from 'ArrayRef[HashRef]' => via {
    [ map { Bio::Metadata::Attribute->new($_) } @$_ ];
},
  from 'Bio::Metadata::Attribute' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Attribute->new($_) ];
  };

#entity
class_type 'Bio::Metadata::Entity';

coerce 'Bio::Metadata::Entity' => from 'HashRef' =>
  via { Bio::Metadata::Entity->new($_); };

subtype 'Bio::Metadata::EntityArrayRef' => as 'ArrayRef[Bio::Metadata::Entity]';

coerce 'Bio::Metadata::EntityArrayRef' => from 'ArrayRef[HashRef]' => via {
    [ map { Bio::Metadata::Entity->new($_) } @$_ ];
},
  from 'Bio::Metadata::Entity' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Entity->new($_) ];
  };

#rule
class_type 'Bio::Metadata::Rules::Rule';
coerce 'Bio::Metadata::Rules::Rule' => from 'HashRef' =>
  via { Bio::Metadata::Rules::Rule->new($_); };

subtype 'Bio::Metadata::Rules::RuleArrayRef' => as
  'ArrayRef[Bio::Metadata::Rules::Rule]';

coerce 'Bio::Metadata::Rules::RuleArrayRef' => from 'ArrayRef[HashRef]' => via {
    [ map { Bio::Metadata::Rules::Rule->new($_) } @$_ ];
},
  from 'Bio::Metadata::Rules::Rule' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Rules::Rule->new($_) ];
  };

#rule group
class_type 'Bio::Metadata::Rules::RuleGroup';
coerce 'Bio::Metadata::Rules::RuleGroup' => from 'HashRef' =>
  via { Bio::Metadata::Rules::RuleGroup->new($_); };

subtype 'Bio::Metadata::Rules::RuleGroupArrayRef' => as
  'ArrayRef[Bio::Metadata::Rules::RuleGroup]';

coerce 'Bio::Metadata::Rules::RuleGroupArrayRef' => from 'ArrayRef[HashRef]' =>
  via {
    [ map { Bio::Metadata::Rules::RuleGroup->new($_) } @$_ ];
  },
  from 'Bio::Metadata::Rules::RuleGroup' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Rules::RuleGroup->new($_) ];
  };

#condition
class_type 'Bio::Metadata::Rules::Condition';
coerce 'Bio::Metadata::Rules::Condition' => from
  'HashRef' => via { Bio::Metadata::Rules::Condition->new($_); },
  from 'Str ' =>
  via { Bio::Metadata::Rules::Condition->new( dpath_condition => $_ ); };

subtype 'Bio::Metadata::Rules::ConditionArrayRef' => as
  'ArrayRef[Bio::Metadata::Rules::Condition]';

coerce 'Bio::Metadata::Rules::ConditionArrayRef' => from 'ArrayRef[HashRef]' =>
  via {
    [ map { Bio::Metadata::Rules::Condition->new($_) } @$_ ];
  },
  from 'Bio::Metadata::Rules::Condition' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Rules::Condition->new($_) ];
  },
  from 'Str' =>
  via { [ Bio::Metadata::Rules::Condition->new( dpath_condition => $_ ) ] };

#validation outcome
class_type 'Bio::Metadata::Validate::ValidationOutcome';
coerce 'Bio::Metadata::Validate::ValidationOutcome' => from 'HashRef' =>
  via { Bio::Metadata::Validate::ValidationOutcome->new($_); };

subtype 'Bio::Metadata::Validate::ValidationOutcomeArrayRef' => as
  'ArrayRef[Bio::Metadata::Validate::ValidationOutcome]';

coerce 'Bio::Metadata::Validate::ValidationOutcomeArrayRef' => from
  'ArrayRef[HashRef]'                                       => via {
    [ map { Bio::Metadata::Validate::ValidationOutcome->new($_) } @$_ ];
  },
  from 'Bio::Metadata::Validate::ValidationOutcome' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::Validate::ValidationOutcome->new($_) ];
  };

#validationschema
enum 'Bio::Metadata::ValidateSchema::OutcomeEnum', [qw(pass warning)];

#validationschema outcome
class_type 'Bio::Metadata::ValidateSchema::ValidationOutcome';
coerce 'Bio::Metadata::ValidateSchema::ValidationOutcome' => from 'HashRef' =>
  via { Bio::Metadata::ValidateSchema::ValidationOutcome->new($_); };

subtype 'Bio::Metadata::ValidateSchema::ValidationOutcomeArrayRef' => as
  'ArrayRef[Bio::Metadata::ValidateSchema::ValidationOutcome]';

coerce 'Bio::Metadata::ValidateSchema::ValidationOutcomeArrayRef' => from
  'ArrayRef[HashRef]'                                             => via {
    [ map { Bio::Metadata::ValidateSchema::ValidationOutcome->new($_) } @$_ ];
  },
  from 'Bio::Metadata::ValidateSchema::ValidationOutcome' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::ValidateSchema::ValidationOutcome->new($_) ];
  };

#warning
class_type 'Bio::Metadata::ValidateSchema::Warning';

coerce 'Bio::Metadata::ValidateSchema::Warning' => from 'HashRef' =>
  via { Bio::Metadata::Warning->new($_); };

subtype 'Bio::Metadata::ValidateSchema::WarningArrayRef' => as
  'ArrayRef[Bio::Metadata::ValidateSchema::Warning]';

coerce 'Bio::Metadata::ValidateSchema::WarningArrayRef' => from
  'ArrayRef[HashRef]'                                   => via {
    [ map { Bio::Metadata::Warning->new($_) } @$_ ];
  },
  from 'Bio::Metadata::ValidateSchema::Warning' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Metadata::ValidateSchema::Warning->new($_) ];
  };

class_type 'Bio::Metadata::Validate::Support::OlsLookup';

1;
