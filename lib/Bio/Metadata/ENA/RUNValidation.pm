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
package Bio::Metadata::ENA::RUNValidation;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Validate::EntityValidator;

has 'run_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'Run XML section - run',
      rule_groups => [
        {
          name  => 'Run rules',
          rules => [
            {
              name      => 'alias',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'run_center',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'run_date',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'EXPERIMENT_REF',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'filename',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'filetype',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'checksum_method',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'checksum',
              mandatory => 'mandatory',
              type      => 'text'
            },
                        {
              name      => 'filename_pair',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'filetype_pair',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'checksum_method_pair',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'checksum_pair',
              mandatory => 'optional',
              type      => 'text'
            },
          ]
        },
      ]
    };
  }
);

sub validate_run {
  my ( $self, $run_entries ) = @_;

  my %blocks;
  for my $run_entity (@$run_entries) {
    $blocks{ $run_entity->id } //= [];
    push @{ $blocks{ $run_entity->id } }, $run_entity;
  }

  my @errors;
  push @errors,
    $self->validate_section( \%blocks, $self->run_rule_set);

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $rule_set) = @_;

  my @rows = keys(%$blocks);

  if ( scalar(@rows) == 0 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "At least one run required",
      rule =>
        Bio::Metadata::Rules::Rule->new( name => "run", type => 'text' ),
    );
  }

  my $v = Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  my @errors;
  foreach my $row (@rows){
    my $entities = $blocks->{$row} || [];
    for my $e (@$entities) {
      my ( $outcome_overall, $validation_outcomes ) = $v->check($e);
      push @errors, grep { $_->outcome ne 'pass' } @$validation_outcomes;
      push @errors, &checkLimitedValues($e); 
    }
  }
  return @errors;
}

sub checkLimitedValues(){
  my $entity = $_[0];
  my @errors;
  foreach my $attr(@{$entity->attributes}){
    if($attr->name eq "checksum_method"){
      unless ($attr->value eq "MD5" || $attr->value eq "SHA-256"){
        push @errors, Bio::Metadata::Validate::ValidationOutcome->new(
          outcome => 'error',
          message => "checksum_method value can only be MD5 or SHA-256 according to ENA rule",
          rule =>
            Bio::Metadata::Rules::Rule->new( name => "run", type => 'text' ),
        );
      }
    }
  }
  return @errors;
}

__PACKAGE__->meta->make_immutable;
1;