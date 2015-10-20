
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

package Bio::Validate::Types;

use strict;
use warnings;
use Carp;
use Moose::Util::TypeConstraints;

enum 'Bio::Rules::Rule::TypeEnum',[qw(text number enum)];
enum 'Bio::Rules::Rule::MandatoryEnum',[qw(mandatory recommended optional)];

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
class_type 'Bio::Rules::Rule';
coerce 'Bio::Rules::Rule' => from 'HashRef' =>
  via { Bio::Rules::Rule->new($_); };

subtype 'Bio::Rules::RuleArrayRef' => as 'ArrayRef[Bio::Rules::Rule]';

coerce 'Bio::Rules::RuleArrayRef' => from 'ArrayRef[HashRef]' => via {
    [ map { Bio::Rules::Rule->new($_) } @$_ ];
},
  from 'Bio::Rules::Rule' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Rules::Rule->new($_) ];
  };

#rule group
class_type 'Bio::Rules::RuleGroup';
coerce 'Bio::Rules::RuleGroup' => from 'HashRef' =>
  via { Bio::Rules::RuleGroup->new($_); };

subtype 'Bio::Rules::RuleGroupArrayRef' => as 'ArrayRef[Bio::Rules::RuleGroup]';

coerce 'Bio::Rules::RuleGroupArrayRef' => from 'ArrayRef[HashRef]' => via {
    [ map { Bio::Rules::RuleGroup->new($_) } @$_ ];
},
  from 'Bio::Rules::RuleGroup' => via {
    [$_];
  },
  from 'HashRef' => via {
    [ Bio::Rules::RuleGroup->new($_) ];
  };

1;
