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
package Bio::Metadata::ENA::EXPRValidation;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Rules::RuleSet;
use Bio::Metadata::Rules::Rule;
use Bio::Metadata::Validate::ValidationOutcome;
use Bio::Metadata::Validate::EntityValidator;

has 'ena_rule_set' => (
  is      => 'ro',
  isa     => 'Bio::Metadata::Rules::RuleSet',
  coerce  => 1,
  default => sub {
    {
      name        => 'ENA XML section - ena',
      rule_groups => [
        {
          name  => 'ENA rules',
          rules => [
            {
              name      => 'SAMPLE_DESCRIPTOR',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'EXPERIMENT_alias',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'TITLE',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'STUDY_REF',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'DESIGN_DESCRIPTION',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_NAME',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_STRATEGY',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_SOURCE',
              mandatory => 'mandatory',
              type      => 'text'
            },
                        {
              name      => 'LIBRARY_SELECTION',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_LAYOUT',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'NOMINAL_LENGTH',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'NOMINAL_SDEV',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'LIBRARY_CONSTRUCTION_PROTOCOL',
              mandatory => 'optional',
              type      => 'text'
            },
            {
              name      => 'PLATFORM',
              mandatory => 'mandatory',
              type      => 'text'
            },
            {
              name      => 'INSTRUMENT_MODEL',
              mandatory => 'optional',
              type      => 'text'
            },
          ]
        },
      ]
    };
  }
);

my @typeLibraryStrategy = qw/WGS WGA WXS RNA-Seq ssRNA-seq miRNA-Seq ncRNA-Seq FL-cDNA EST Hi-C  ATAC-seq  WCS RAD-Seq CLONE POOLCLONE AMPLICON  CLONEEND  FINISHING ChIP-Seq  MNase-Seq DNase-Hypersensitivity  Bisulfite-Seq CTS MRE-Seq MeDIP-Seq MBD-Seq Tn-Seq  VALIDATION  FAIRE-seq SELEX RIP-Seq ChIA-PET  Synthetic-Long-Read Targeted-Capture  Tethered Chromatin Conformation Capture OTHER/;
my @typeLibrarySource = qw/GENOMIC GENOMIC SINGLE CELL TRANSCRIPTOMIC  TRANSCRIPTOMIC SINGLE CELL  METAGENOMIC METATRANSCRIPTOMIC  SYNTHETIC VIRAL RNA OTHER/;
my @typeLibrarySelection = qw/RANDOM  PCR RANDOM PCR  RT-PCR  HMPR  MF  repeat fractionation  size fractionation  MSLL  cDNA  cDNA_randomPriming  cDNA_oligo_dT PolyA Oligo-dT  Inverse rRNA  Inverse rRNA selection  ChIP  ChIP-Seq  MNase DNase Hybrid Selection  Reduced Representation  Restriction Digest  5-methylcytidine antibody MBD2 protein methyl-CpG binding domain  CAGE  RACE  MDA padlock probes capture method other unspecified/;
my @libraryLayout = qw/PAIRED  SINGLE/;
my %typeLibraryStrategy = &convertArrayToHash(\@typeLibraryStrategy);
my %typeLibrarySource = &convertArrayToHash(\@typeLibrarySource);
my %typeLibrarySelection = &convertArrayToHash(\@typeLibrarySelection);
my %libraryLayout = &convertArrayToHash(\@libraryLayout);

sub convertArrayToHash(){
  my @in = @{$_[0]};
  my %result;
  foreach (@in){
    $result{$_} = 1;
  }
  return %result;
}

sub validate_expr {
  my ( $self, $expr_entries ) = @_;

  my %blocks;
  for my $expr_entity (@$expr_entries) {
    $blocks{ $expr_entity->id } //= [];
    push @{ $blocks{ $expr_entity->id } }, $expr_entity;
  }

  my @errors;
  push @errors,
    $self->validate_section( \%blocks, $self->ena_rule_set);

  return \@errors;
}

sub validate_section {
  my ( $self, $blocks, $rule_set) = @_;

  my @rows = keys(%$blocks);

  if ( scalar(@rows) == 0 ) {
    return Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "At least one ENA experiment row required",
      rule =>
        Bio::Metadata::Rules::Rule->new( name => "experiment_ena", type => 'text' ),
    );
  }

  my $v = Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  my @errors;
  my %errors;
  foreach my $row (@rows){
    my $entities = $blocks->{$row} || [];
    for my $e (@$entities) {
      my ( $outcome_overall, $validation_outcomes ) = $v->check($e);
      push @errors, grep { $_->outcome ne 'pass' } @$validation_outcomes;
      my @limitedErrors = &checkLimitedValues($e);
      foreach my $limitedError(@limitedErrors){
        $errors{$limitedError}++;
      } 
    }
  }
  foreach my $limitedError(keys %errors){
    push @errors, Bio::Metadata::Validate::ValidationOutcome->new(
      outcome => 'error',
      message => "$limitedError: occuring $errors{$limitedError} times",
      rule =>
        Bio::Metadata::Rules::Rule->new( name => "run", type => 'text' ),
    );
  }
  return @errors;
}

sub checkLimitedValues(){
  my $entity = $_[0];
  my @errorMsgs;
  foreach my $attr(@{$entity->attributes}){
    my $value = $attr->value;
    if($attr->name eq "LIBRARY_STRATEGY"){
      push @errorMsgs,"Wrong library strategy value $value, only could be one of @typeLibraryStrategy" unless (exists $typeLibraryStrategy{$value});
    }
    if($attr->name eq "LIBRARY_SOURCE"){
      push @errorMsgs, "Wrong library source value $value, only could be one of @typeLibrarySource" unless (exists $typeLibrarySource{$value});
    }
    if($attr->name eq "LIBRARY_SELECTION"){
      push @errorMsgs, "Wrong library selection value $value, only could be one of @typeLibrarySelection" unless (exists $typeLibrarySelection{$value});
    }
    if($attr->name eq "LIBRARY_LAYOUT"){
      push @errorMsgs, "Wrong library layout value $value, only could be one of @libraryLayout" unless (exists $libraryLayout{$value});
    }
  }
  return @errorMsgs;
}

__PACKAGE__->meta->make_immutable;
1;