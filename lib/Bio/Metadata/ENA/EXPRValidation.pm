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

my @typeLibraryStrategy = ('WGS', 'WGA', 'WXS', 'RNA-Seq', 'ssRNA-seq', 'miRNA-Seq', 'ncRNA-Seq', 'FL-cDNA', 'EST', 'Hi-C', 'ATAC-seq', 'WCS', 'RAD-Seq', 'CLONE', 'POOLCLONE', 'AMPLICON', 'CLONEEND', 'FINISHING', 'ChIP-Seq', 'MNase-Seq', 'DNase-Hypersensitivity', 'Bisulfite-Seq', 'CTS', 'MRE-Seq', 'MeDIP-Seq', 'MBD-Seq', 'Tn-Seq', 'VALIDATION', 'FAIRE-seq', 'SELEX', 'RIP-Seq', 'ChIA-PET', 'Synthetic-Long-Read', 'Targeted-Capture', 'Tethered Chromatin Conformation Capture', 'OTHER');
my @typeLibrarySource = ('GENOMIC', 'GENOMIC SINGLE CELL', 'TRANSCRIPTOMIC', 'TRANSCRIPTOMIC SINGLE CELL', 'METAGENOMIC', 'METATRANSCRIPTOMIC', 'SYNTHETIC', 'VIRAL RNA', 'OTHER');
my @typeLibrarySelection = ('RANDOM', 'PCR', 'RANDOM PCR', 'RT-PCR', 'HMPR', 'MF', 'repeat fractionation', 'size fractionation', 'MSLL', 'cDNA', 'cDNA_randomPriming', 'cDNA_oligo_dT', 'PolyA', 'Oligo-dT', 'Inverse rRNA', 'Inverse rRNA selection', 'ChIP', 'ChIP-Seq', 'MNase', 'DNase', 'Hybrid Selection', 'Reduced Representation', 'Restriction Digest', '5-methylcytidine antibody', 'MBD2 protein methyl-CpG binding domain', 'CAGE', 'RACE', 'MDA', 'padlock probes capture method', 'other', 'unspecified');
my @libraryLayout = qw/PAIRED  SINGLE/; 
my @platformType = qw/ION_TORRENT BGISEQ  CAPILLARY OXFORD_NANOPORE ILLUMINA COMPLETE_GENOMICS ABI_SOLID HELICOS LS454 PACBIO_SMRT/;
my %typeLibraryStrategy = &convertArrayToHash(\@typeLibraryStrategy);
my %typeLibrarySource = &convertArrayToHash(\@typeLibrarySource);
my %typeLibrarySelection = &convertArrayToHash(\@typeLibrarySelection);
my %libraryLayout = &convertArrayToHash(\@libraryLayout);
my %platformType = &convertArrayToHash(\@platformType);
$"=",";

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
        Bio::Metadata::Rules::Rule->new( name => "experiment_ena", type => 'text' ),
    );
  }
  return @errors;
}

sub checkLimitedValues(){
  my $entity = $_[0];
  my @errorMsgs;
  my $platform = "";
  my $model = "";
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
      $model = $value;
      push @errorMsgs, "Wrong library layout value $value, only could be one of @libraryLayout" unless (exists $libraryLayout{$value});
    }
    if($attr->name eq "PLATFORM"){
      push @errorMsgs, "Wrong library layout value $value, only could be one of @libraryLayout" unless (exists $libraryLayout{$value});
    }
    $model = $value if($attr->name eq "INSTRUMENT_MODEL");
  }
  my $modelCheck = &checkModel($platform,$model);
  push @errorMsgs,$modelCheck unless (length($modelCheck) == 0);
  return @errorMsgs;
}

sub checkModel(){
  my $result = "";
  my @type454Model = ('454 GS', '454 GS 20', '454 GS FLX', '454 GS FLX+', '454 GS FLX Titanium', '454 GS Junior', 'unspecified');
  my @typeIlluminaModel = ('HiSeq X Five', 'HiSeq X Ten', 'Illumina Genome Analyzer', 'Illumina Genome Analyzer II', 'Illumina Genome Analyzer IIx', 'Illumina HiScanSQ', 'Illumina HiSeq 1000', 'Illumina HiSeq 1500', 'Illumina HiSeq 2000', 'Illumina HiSeq 2500', 'Illumina HiSeq 3000', 'Illumina HiSeq 4000', 'Illumina MiSeq', 'Illumina MiniSeq', 'Illumina NovaSeq 6000', 'NextSeq 500', 'NextSeq 550', 'unspecified');
  my @typeHelicosModel = ('Helicos HeliScope', 'unspecified');
  my @typeAbiSolidModel = ('AB SOLiD System', 'AB SOLiD System 2.0', 'AB SOLiD System 3.0', 'AB SOLiD 3 Plus System', 'AB SOLiD 4 System', 'AB SOLiD 4hq System', 'AB SOLiD PI System', 'AB 5500 Genetic Analyzer', 'AB 5500xl Genetic Analyzer', 'AB 5500xl-W Genetic Analysis System', 'unspecified');
  my @typeCGModel = ('Complete Genomics', 'unspecified');
  my @typeBGISEQModel = ('BGISEQ-500');
  my @typePacBioModel = ('PacBio RS', 'PacBio RS II', 'Sequel', 'unspecified');
  my @typeIontorrentModel = ('Ion Torrent PGM', 'Ion Torrent Proton', 'Ion Torrent S5', 'Ion Torrent S5 XL', 'unspecified');
  my @typeCapillaryModel = ('AB 3730xL Genetic Analyzer', 'AB 3730 Genetic Analyzer', 'AB 3500xL Genetic Analyzer', 'AB 3500 Genetic Analyzer', 'AB 3130xL Genetic Analyzer', 'AB 3130 Genetic Analyzer', 'AB 310 Genetic Analyzer', 'unspecified');
  my @typeOxfordNanoporeModel = ('MinION', 'GridION', 'PromethION', 'unspecified');
  my %type454Model = &convertArrayToHash(\@type454Model);
  my %typeIlluminaModel = &convertArrayToHash(\@typeIlluminaModel);
  my %typeHelicosModel = &convertArrayToHash(\@typeHelicosModel);
  my %typeAbiSolidModel = &convertArrayToHash(\@typeAbiSolidModel);
  my %typeCGModel = &convertArrayToHash(\@typeCGModel);
  my %typeBGISEQModel = &convertArrayToHash(\@typeBGISEQModel);
  my %typePacBioModel = &convertArrayToHash(\@typePacBioModel);
  my %typeIontorrentModel = &convertArrayToHash(\@typeIontorrentModel);
  my %typeCapillaryModel = &convertArrayToHash(\@typeCapillaryModel);
  my %typeOxfordNanoporeModel = &convertArrayToHash(\@typeOxfordNanoporeModel);
  my ($platform,$model) = @_;
  if ($platform eq "ION_TORRENT"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeIontorrentModel" unless (exists $typeIontorrentModel{$model});
  }elsif ($platform eq "BGISEQ"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeBGISEQModel" unless (exists $typeBGISEQModel{$model});
  }elsif ($platform eq "CAPILLARY"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeCapillaryModel" unless (exists $typeCapillaryModel{$model});
  }elsif ($platform eq "OXFORD_NANOPORE"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeOxfordNanoporeModel" unless (exists $typeOxfordNanoporeModel{$model});
  }elsif ($platform eq "ILLUMINA"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeIlluminaModel" unless (exists $typeIlluminaModel{$model});
  }elsif ($platform eq "COMPLETE_GENOMICS"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeCGModel" unless (exists $typeCGModel{$model});
  }elsif ($platform eq "ABI_SOLID"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeAbiSolidModel" unless (exists $typeAbiSolidModel{$model});
  }elsif ($platform eq "HELICOS"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typeHelicosModel" unless (exists $typeHelicosModel{$model});
  }elsif ($platform eq "PACBIO_SMRT"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @typePacBioModel" unless (exists $typePacBioModel{$model});
  }elsif ($platform eq "LS454"){
    $result = "Wrong model ($model) for given platform $platform, should be one of @type454Model" unless (exists $type454Model{$model});
  }
  return $result;
}

__PACKAGE__->meta->make_immutable;
1;