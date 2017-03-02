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
package Bio::Metadata::ENA::XML;

use strict;
use warnings;
use Data::Dumper;
use utf8;
use Moose;
use namespace::autoclean;
use Bio::Metadata::Loader::XLSXExperimentLoader;
use Moose::Util::TypeConstraints;

use Bio::Metadata::ENA::SUBValidation;
use Bio::Metadata::ENA::STDValidation;
use Bio::Metadata::ENA::EXPRValidation;
use Bio::Metadata::ENA::RUNValidation;
use Bio::Metadata::Reporter::BasicReporter;

has 'rule_set' => (
  is  => 'rw',
  isa => 'Bio::Metadata::Rules::RuleSet'
);

has 'sub' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_sub   => 'elements',
    add_sub   => 'push',
    count_sub => 'count',
    get_sub   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'std' => (
 traits  => ['Array'],
 is      => 'rw',
 isa     => 'Bio::Metadata::EntityArrayRef',
 handles => {
   all_std   => 'elements',
   add_std   => 'push',
   count_std => 'count',
   get_std   => 'get',
 },
 default => sub { [] },
 coerce  => 1,
);

has 'expr' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_expr   => 'elements',
    add_expr   => 'push',
    count_expr => 'count',
    get_expr   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'exprfaang' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_exprfaang   => 'elements',
    add_exprfaang   => 'push',
    count_exprfaang => 'count',
    get_exprfaang   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'run' => (
  traits  => ['Array'],
  is      => 'rw',
  isa     => 'Bio::Metadata::EntityArrayRef',
  handles => {
    all_run   => 'elements',
    add_run   => 'push',
    count_run => 'count',
    get_run   => 'get',
  },
  default => sub { [] },
  coerce  => 1,
);

has 'sub_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::SUBValidation',
  default => sub { Bio::Metadata::ENA::SUBValidation->new },
);

has 'std_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::STDValidation',
  default => sub { Bio::Metadata::ENA::STDValidation->new },
);

has 'expr_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::EXPRValidation',
  default => sub { Bio::Metadata::ENA::EXPRValidation->new },
);

has 'run_validator' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::ENA::RUNValidation',
  default => sub { Bio::Metadata::ENA::RUNValidation->new },
);

sub read {
  my ( $self, $file_path ) = @_;

  die("[ERROR] Please provide the path to a XLSX file") if !$file_path;

  my $loader = Bio::Metadata::Loader::XLSXExperimentLoader->new();

  $self->sub( $loader->load_sub_entities($file_path) );
  $self->std( $loader->load_std_entities($file_path) );
  $self->exprfaang( $loader->load($file_path) );
  $self->expr( $loader->load_exprena_entities($file_path) );
  $self->run( $loader->load_run_entities($file_path) );
}

sub validate {
  my ($self) = @_;
  my $sub_errors = $self->sub_validator->validate_sub( $self->sub );
  my $std_errors = $self->std_validator->validate_std( $self->std );
  my $expr_errors = $self->expr_validator->validate_expr( $self->expr );
  my $run_errors = $self->run_validator->validate_run( $self->run );
  push @$sub_errors, @$std_errors, @$run_errors, @$expr_errors;
  return $sub_errors;
}

sub report_sub {
  my ($self) = @_;

  my $xml_header ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
  my $sub_header ="<SUBMISSION_SET xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.submission.xsd\">\n";
  my $sub_footer ="</SUBMISSION_SET>";

  my $output = $xml_header.$sub_header;

  my ($alias, $center_name, @actions, $holduntil);
  my %schema = (
    "STUDY XML FILENAME" => "study",
    "EXPERIMENT XML FILENAME" => "experiment",
    "RUN XML FILENAME" => "run",
  );
  for my $e ( $self->all_sub ) {
    for my $a ($e->all_attributes) {

      next if ! defined $a->value;

      if ($a->name eq 'alias'){
        $alias = $a->value;
      }
      elsif ($a->name eq 'center_name'){
        $center_name = $a->value;
      }
      elsif($a->name eq "STUDY XML FILENAME" || $a->name eq "EXPERIMENT XML FILENAME" || $a->name eq "RUN XML FILENAME"){
        push(@actions, "\t\t\t<ACTION>\n");
        push(@actions, "\t\t\t\t<ADD source=\"".$a->value."\" schema=\"".$schema{$a->name}."\"/>\n");
        push(@actions, "\t\t\t</ACTION>\n");
      }elsif ($a->name eq 'HoldUntilDate'){
        $holduntil = $a->value;
      }
    }
  }

  $output = $output."\t<SUBMISSION alias=\"".$alias."\" center_name=\"".$center_name."\">\n";
  $output = $output."\t\t<ACTIONS>\n";
  $output = $output.join("", @actions);
  if ($holduntil){
    $output = $output."\t\t\t<ACTION>\n\t\t\t\t<HOLD>\n\t\t\t\t\t<HoldUntilDate=\"".$holduntil."\"/>\n\t\t\t\t</HOLD>\n\t\t\t</ACTION>\n";
  }else{
    $output = $output."\t\t\t<ACTION>\n\t\t\t\t<RELEASE/>\n\t\t\t</ACTION>\n";
  }
  $output = $output."\t\t</ACTIONS>\n\t</SUBMISSION>\n".$sub_footer;
}

sub report_std {
  my ($self) = @_;
  my $xml_header ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
  my $std_header ="<STUDY_SET xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.study.xsd\">\n";
  my $std_footer ="</STUDY_SET>";

  my ($study_alias, $center_name, $STUDY_TITLE, $STUDY_TYPE, $STUDY_DESCRIPTION);

  my $output = $xml_header.$std_header;

  for my $e ( $self->all_std ) {
    for my $a ($e->all_attributes) {

      next if ! defined $a->value;

      if ($a->name eq 'study_alias'){
        $study_alias = $a->value;
      }
      elsif ($a->name eq 'center_name'){
        $center_name = $a->value;
      }
      elsif ($a->name eq 'STUDY_TITLE'){
        $STUDY_TITLE = $a->value;
      }
      elsif ($a->name eq 'STUDY_TYPE'){
        $STUDY_TYPE = $a->value;
      }
      elsif ($a->name eq 'STUDY_DESCRIPTION'){
        $STUDY_DESCRIPTION = $a->value;
      }
    }
  }
  $output = $output."\t<STUDY alias=\"".$study_alias."\" center_name=\"".$center_name."\">\n";
  $output = $output."\t\t<DESCRIPTOR>\n";
  $output = $output."\t\t\t<STUDY_TITLE>".$STUDY_TITLE."</STUDY_TITLE>\n";
  $output = $output."\t\t\t<STUDY_TYPE existing_study_type=\"".$STUDY_TYPE."\"/>\n";
  $output = $output."\t\t\t<STUDY_DESCRIPTION>".$STUDY_DESCRIPTION."</STUDY_DESCRIPTION>\n";
  $output = $output."\t\t</DESCRIPTOR>\n";
  $output = $output.$std_footer;
}

sub report_expr {
  my ($self) = @_;
  my $xml_header ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
  my $expr_header ="<EXPERIMENT_SET xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.experiment.xsd\">\n";
  my $expr_footer ="</EXPERIMENT_SET>";

  my (@experiments, %attributes);

  my $output = $xml_header.$expr_header;

  for my $e ( $self->all_exprfaang ) {
    my ($attribute_block, $EXPERIMENT_alias);
    for my $a ($e->all_attributes) {
      next if ! defined $a->value;
      $attribute_block = $attribute_block."\t\t\t<EXPERIMENT_ATTRIBUTE>\n";
      $attribute_block = $attribute_block."\t\t\t\t<TAG>".$a->name."</TAG>\n";
      $attribute_block = $attribute_block."\t\t\t\t<VALUE>".$a->value."</VALUE>\n";
      if ($a->units){
        $attribute_block = $attribute_block."\t\t\t\t<UNITS>".$a->units."</UNITS>\n";
      }
      $attribute_block = $attribute_block."\t\t\t</EXPERIMENT_ATTRIBUTE>\n";
    }
    $attributes{$e->id}=$attribute_block;
  }
  for my $e ( $self->all_expr ) {
    my ($EXPERIMENT_alias, $center_name, $SAMPLE_DESCRIPTOR, $TITLE, $STUDY_REF, $LIBRARY_NAME, $LIBRARY_STRATEGY, $LIBRARY_SOURCE, $LIBRARY_SELECTION, $LIBRARY_LAYOUT, $NOMINAL_LENGTH, $NOMINAL_SDEV, $LIBRARY_CONSTRUCTION_PROTOCOL, $PLATFORM, $INSTRUMENT_MODEL);
    for my $a ($e->all_attributes) {
      next if ! defined $a->value;
      if ($a->name eq 'EXPERIMENT_alias'){
        $EXPERIMENT_alias = $a->value;
      }
      elsif ($a->name eq 'center_name'){
        $center_name = $a->value;
      }
      elsif ($a->name eq 'SAMPLE_DESCRIPTOR'){
        $SAMPLE_DESCRIPTOR = $a->value;
      }
      elsif ($a->name eq 'TITLE'){
        $TITLE = $a->value;
      }
      elsif ($a->name eq 'STUDY_REF'){
        $STUDY_REF = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_NAME'){
        $LIBRARY_NAME = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_STRATEGY'){
        $LIBRARY_STRATEGY = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_SOURCE'){
        $LIBRARY_SOURCE = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_SELECTION'){
        $LIBRARY_SELECTION = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_LAYOUT'){
        $LIBRARY_LAYOUT = $a->value;
      }
      elsif ($a->name eq 'NOMINAL_LENGTH'){
        $NOMINAL_LENGTH = $a->value;
      }
      elsif ($a->name eq 'NOMINAL_SDEV'){
        $NOMINAL_SDEV = $a->value;
      }
      elsif ($a->name eq 'LIBRARY_CONSTRUCTION_PROTOCOL'){
        $LIBRARY_CONSTRUCTION_PROTOCOL = $a->value;
      }
      elsif ($a->name eq 'PLATFORM'){
        $PLATFORM = $a->value;
      }
      elsif ($a->name eq 'INSTRUMENT_MODEL'){
        $INSTRUMENT_MODEL = $a->value;
      }
    }
    my $experiment = "\t<EXPERIMENT alias=\"".$EXPERIMENT_alias."\" center_name=\"".$center_name."\">\n";
    $experiment = $experiment."\t\t<TITLE>".$TITLE."</TITLE>\n";
    $experiment = $experiment."\t\t<STUDY_REF refname =\"".$STUDY_REF."\"/>\n";
    $experiment = $experiment."\t\t<DESIGN>\n\t\t\t<SAMPLE_DESCRIPTOR refname =\"".$SAMPLE_DESCRIPTOR."\"/>\n";
    $experiment = $experiment."\t\t\t<LIBRARY_DESCRIPTOR>\n";
    $experiment = $experiment."\t\t\t\t<LIBRARY_NAME>".$LIBRARY_NAME."</LIBRARY_NAME>\n";
    $experiment = $experiment."\t\t\t\t<LIBRARY_STRATEGY>".$LIBRARY_STRATEGY."</LIBRARY_STRATEGY>\n";
    $experiment = $experiment."\t\t\t\t<LIBRARY_SOURCE>".$LIBRARY_SOURCE."</LIBRARY_SOURCE>\n";
    $experiment = $experiment."\t\t\t\t<LIBRARY_SELECTION>".$LIBRARY_SELECTION."</LIBRARY_SELECTION>\n";
    if ($NOMINAL_LENGTH){
      if ($NOMINAL_SDEV){
        $experiment = $experiment."\t\t\t\t<LIBRARY_LAYOUT>\n\t\t\t\t\t<".$LIBRARY_LAYOUT." NOMINAL_LENGTH=\"".$NOMINAL_LENGTH."\" NOMINAL_SDEV=\"".$NOMINAL_SDEV."\">\n\t\t\t\t</LIBRARY_LAYOUT>\n";
      }else{
        $experiment = $experiment."\t\t\t\t<LIBRARY_LAYOUT>\n\t\t\t\t\t<".$LIBRARY_LAYOUT." NOMINAL_LENGTH=\"".$NOMINAL_LENGTH."\">\n\t\t\t\t</LIBRARY_LAYOUT>\n";
      }
    }elsif ($NOMINAL_SDEV){
      $experiment = $experiment."\t\t\t\t<LIBRARY_LAYOUT>\n\t\t\t\t\t<".$LIBRARY_LAYOUT." NOMINAL_SDEV=\"".$NOMINAL_SDEV."\">\n\t\t\t\t</LIBRARY_LAYOUT>\n";
    }else{
      $experiment = $experiment."\t\t\t\t<LIBRARY_LAYOUT>\n\t\t\t\t\t<".$LIBRARY_LAYOUT.">\n\t\t\t\t</LIBRARY_LAYOUT>\n";
    }
    if ($LIBRARY_CONSTRUCTION_PROTOCOL){
      $experiment = $experiment."\t\t\t\t<LIBRARY_CONSTRUCTION_PROTOCOL>".$LIBRARY_CONSTRUCTION_PROTOCOL."</LIBRARY_CONSTRUCTION_PROTOCOL>\n";
    }
    if ($PLATFORM){
      if ($INSTRUMENT_MODEL){
        $experiment = $experiment."\t\t\t\t<PLATFORM>\n\t\t\t\t\t<".$PLATFORM.">\n\t\t\t\t\t\t<INSTRUMENT_MODEL>".$INSTRUMENT_MODEL."</INSTRUMENT_MODEL>\n\t\t\t\t\t</".$PLATFORM.">\n\t\t\t\t</PLATFORM>\n";
      }else{
        $experiment = $experiment."\t\t\t\t<PLATFORM>\n\t\t\t\t\t<".$PLATFORM."/>\n\t\t\t\t</PLATFORM>\n";
      }
    }
    $experiment = $experiment."\t\t\t</LIBRARY_DESCRIPTOR>\n\t\t</DESIGN>\n";
    $experiment = $experiment."\t\t<EXPERIMENT_ATTRIBUTES>\n";
    $experiment = $experiment.$attributes{$EXPERIMENT_alias};
    $experiment = $experiment."\t\t</EXPERIMENT_ATTRIBUTES>\n";
    push(@experiments, $experiment);
  }
  foreach my $experiment (@experiments){
    $output = $output.$experiment;
  }
  $output=$output.$expr_footer;
}

sub report_run {
  my ($self) = @_;
  my $xml_header ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
  my $run_header ="<RUN_SET xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.run.xsd\">\n";
  my $run_footer ="</RUN_SET>";

  my @runs;

  my $output = $xml_header.$run_header;

  for my $e ( $self->all_run ) {
    my ($alias, $center_name, $run_center, $run_date, $EXPERIMENT_REF, $filename, $filetype, $checksum_method, $checksum, $filename_pair, $filetype_pair, $checksum_method_pair, $checksum_pair);
    for my $a ($e->all_attributes) {
      next if ! defined $a->value;
      if ($a->name eq 'alias'){
        $alias = $a->value;
      }
      elsif ($a->name eq 'center_name'){
        $center_name = $a->value;
      }
      elsif ($a->name eq 'run_center'){
        $run_center = $a->value;
      }
      elsif ($a->name eq 'run_date'){
        $run_date = $a->value;
      }
      elsif ($a->name eq 'EXPERIMENT_REF'){
        $EXPERIMENT_REF = $a->value;
      }
      elsif ($a->name eq 'filename'){
        $filename = $a->value;
      }
      elsif ($a->name eq 'filetype'){
        $filetype = $a->value;
      }
      elsif ($a->name eq 'checksum_method'){
        $checksum_method = $a->value;
      }
      elsif ($a->name eq 'checksum'){
        $checksum = $a->value;
      }
      elsif ($a->name eq 'filename_pair'){
        $filename_pair = $a->value;
      }
      elsif ($a->name eq 'filetype_pair'){
        $filetype_pair = $a->value;
      }
      elsif ($a->name eq 'checksum_method_pair'){
        $checksum_method_pair = $a->value;
      }
      elsif ($a->name eq 'checksum_pair'){
        $checksum_pair = $a->value;
      }
    }
    my $run = "\t<SUBMISSION alias=\"".$alias."\" center_name=\"".$center_name."\" run_center=\"".$run_center."\" run_date=\"".$run_date."\">\n";
    $run = $run."\t\t<EXPERIMENT_REF refname=\"".$EXPERIMENT_REF."\"/>\n";
    $run = $run."\t\t<DATA_BLOCK>\n";
    $run = $run."\t\t\t<FILES>\n";
    $run = $run."\t\t\t\t<FILE filename=\"".$filename."\" filetype=\"".$filetype."\" checksum_method=\"".$checksum_method."\" checksum=\"".$checksum."\"</FILE>\n";
    if ($filename_pair){
      $run = $run."\t\t\t\t<FILE filename=\"".$filename_pair."\" filetype=\"".$filetype_pair."\" checksum_method=\"".$checksum_method_pair."\" checksum=\"".$checksum_pair."\"</FILE>\n";
    }
    $run = $run."\t\t\t</FILES>\n";
    $run = $run."\t\t\t</DATA_BLOCK>\n";
    push(@runs, $run);
  }
  foreach my $run (@runs){
    $output = $output.$run;
  }
  $output = $output.$run_footer;
}

1;