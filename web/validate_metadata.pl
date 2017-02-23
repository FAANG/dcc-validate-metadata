#!/usr/bin/env perl
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
use strict;
use warnings;
use Carp;
use File::Temp qw(tempfile);
use FindBin qw/$Bin/;
use Try::Tiny;
use Mojolicious::Lite;

use Bio::Metadata::Loader::JSONRuleSetLoader;
use Bio::Metadata::Loader::JSONEntityLoader;
use Bio::Metadata::Reporter::ExcelReporter;
use Bio::Metadata::Reporter::BasicReporter;
use Bio::Metadata::Reporter::TextReporter;
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Bio::Metadata::Loader::XLSXExperimentLoader;
use Bio::Metadata::Loader::XMLExperimentLoader;
use Bio::Metadata::BioSample::SampleTab;

plugin 'Config';
plugin 'RenderFile';

app->secrets( ['nosecrets'] );

my $xlsx_mime_type =
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
my $tsv_mime_type = ' text/tab-separated-values';
app->types->type( xlsx => $xlsx_mime_type, tsv => $tsv_mime_type );

my $brand     = app->config('brand')     || '';
my $brand_img = app->config('brand_img') || '';
app->hook(
  before_render => sub {
    my ( $c, $args ) = @_;
    $c->stash( 'brand',         app->config('brand')         || '' );
    $c->stash( 'brand_img',     app->config('brand_img')     || '' );
    $c->stash( 'resource_name', app->config('resource_name') || '' );
    $c->stash( 'resource_description',
      app->config('resource_description') || '' );
    $c->stash( 'contact_email', app->config('contact_email') || '' );
  }
);

my $loaders = {
  'JSON'               => Bio::Metadata::Loader::JSONEntityLoader->new(),
  'BioSample .xlsx'    => Bio::Metadata::Loader::XLSXBioSampleLoader->new(),
  'SRA Experiment XML' => Bio::Metadata::Loader::XMLExperimentLoader->new(),
  'SRA Experiment .xlsx' => Bio::Metadata::Loader::XLSXExperimentLoader->new(),
};

my $rule_config    = app->config('rules');
my %rule_locations = map { %$_ } @$rule_config;
my @rule_names     = map { keys %$_ } @$rule_config;

my ( $rules, $validators ) = load_rules( \%rule_locations );

my %help_pages = (
  'REST API'             => 'rest',
  'SampleTab conversion' => 'convert',
  'Rule sets'            => 'rule_sets',
  'Validation'           => 'validation',
  'Error explanations'   => 'error_explanations',
  'How to use this site' => 'how_to'
);

get '/' => sub {
  my $c = shift;
  $c->render( template => 'index' );
};

get '/help' => sub {
  my $c = shift;
  $c->stash( 'help_pages', \%help_pages );
  $c->render( template => 'help' );
};

get '/help/#name' => sub {
  my $c    = shift;
  my $name = $c->param('name');
  $c->render( template => 'help_' . $name );
};

get '/rule_sets' => sub {
  my $c = shift;

  $c->respond_to(
    json => sub {
      $c->render( json => { rule_set_names => \@rule_names, } );
    },
    html => sub {
      $c->stash( rule_sets => $rules, rule_set_names => \@rule_names );
      $c->render( template => 'rule_sets' );
    }
  );
};

get '/rule_sets/#name' => sub {
  my $c    = shift;
  my $name = $c->param('name');

  my $rule_set = $rules->{$name};

  return $c->reply->not_found if ( !$rule_set );

  $c->respond_to(
    json => sub {
      $c->render( json => $rule_set->to_hash );
    },
    html => sub {
      $c->stash( rule_set => $rule_set );
      $c->render( template => 'rule_set' );
    }
  );
};

get '/convert' => sub {
  my $c = shift;
  my $supporting_data = { valid_rule_set_names => \@rule_names, };

  $c->respond_to(
    json => sub {
      $c->render( json => $supporting_data );
    },
    html => sub {
      $c->stash(%$supporting_data);
      $c->render(
        template          => 'convert',
        conversion_errors => [],
        status_counts     => {}
      );
    }
  );
};

post '/convert' => sub {
  my $c = shift;

  my $form_validation = $c->validation;
  form_validate_rule_name($form_validation);
  form_validate_metadata_file($form_validation);

  my $rule_set_name = $c->param('rule_set_name');
  my $metadata_file = $c->param('metadata_file');
  my $rule_set      = $rules->{$rule_set_name};

  if ($rule_set_name eq 'FAANG Samples'){
    my $st_converter =
    Bio::Metadata::BioSample::SampleTab->new( rule_set => $rule_set );
    my ( $msi, $scd );
    if ( !$form_validation->has_error ) {
      try {
        my ( $tmp_upload_dir, $tmp_upload_path ) = move_to_tmp($metadata_file);
        $st_converter->read($tmp_upload_path);
      }
      catch {
        $form_validation->error( 'metadata_file' => ['could not parse file'] );
      };
    }

    my $st_errors = $st_converter->validate;
    my $validator = $validators->{$rule_set_name};

    my ($entity_status) = $validator->check_all( $st_converter->scd );

    my %status_counts;
    for ( values %$entity_status ) {
      $status_counts{$_}++;
    }

    if ( $form_validation->has_error || @$st_errors || $status_counts{error} ) {
      sampletab_form_errors( $c, $form_validation, $st_errors, \%status_counts );
    }
    else {
      sampletab_conversion( $c, $st_converter, $rule_set );
    }
  }elsif($rule_set_name eq 'FAANG Samples'){
    my $st_converter =
    Bio::Metadata::ENA::XML->new( rule_set => $rule_set );
  }
};

get '/validate' => sub {
  my $c = shift;

  my $supporting_data = validation_supporting_data();

  $c->respond_to(
    json => sub {
      $c->render( json => $supporting_data );
    },
    html => sub {
      $c->stash(%$supporting_data);
      $c->render( template => 'validate' );
    }
  );
};

post '/validate' => sub {
  my $c = shift;

  my $form_validation = $c->validation;
  form_validate_rule_name($form_validation);
  form_validate_metadata_file($form_validation);

  $form_validation->required('file_format')->in( keys %$loaders );

  my $rule_set_name = $c->param('rule_set_name');
  my $metadata_file = $c->param('metadata_file');
  my $loader        = $loaders->{ $c->param('file_format') };
  my $rule_set      = $rules->{$rule_set_name};

  my $metadata;
  if ( !$form_validation->has_error ) {
    try {
      $metadata = load_metadata( $metadata_file, $loader );
    }
    catch {
      print STDERR "Conversion error:$/" . $_;
      $form_validation->error( 'file_format'   => ['could not parse file'], );
      $form_validation->error( 'metadata_file' => ['could not parse file'] );
    };
  }

  if ( $form_validation->has_error ) {
    validation_form_errors( $c, $form_validation );
  }
  else {
    validate_metadata( $c, $metadata, $rule_set );
  }
};

# Start the Mojolicious command system
app->start;

sub form_validate_metadata_file {
  my ($form_validation) = @_;
  $form_validation->required('metadata_file')
    ->upload->size( 1, 16 * ( 10**6 ) );
}

sub form_validate_rule_name {
  my ($form_validation) = @_;
  $form_validation->required('rule_set_name')->in(@rule_names);
}

sub load_rules {
  my ($rule_locations) = @_;

  my %rules;
  my %validators;

  my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();

  for my $k ( keys %$rule_locations ) {
    my $loc = $rule_locations->{$k};

    if ( !-e $loc && -e "$Bin/$loc" ) {
      $loc = "$Bin/$loc";
    }

    my $rule_set = $loader->load($loc);
    $rules{$k} = $rule_set;
    $validators{$k} =
      Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );
  }

  return ( \%rules, \%validators );
}

sub validation_supporting_data {
  return {
    valid_file_formats   => [ sort keys %$loaders ],
    valid_rule_set_names => \@rule_names,
    valid_output_formats => [
      [ 'Web page' => 'html' ],
      [ 'Excel'    => 'xlsx' ],
      [ 'JSON'     => 'json' ],
      [ 'Text'     => 'txt' ]
    ],
  };
}

sub sampletab_form_errors {
  my ( $c, $form_validation, $st_errors, $status_counts ) = @_;

  my $supporting_data = { valid_rule_set_names => \@rule_names, };

  my %errors =
    map { $_ => $form_validation->error($_) }
    grep { $form_validation->has_error($_) } qw(metadata_file rule_set_name);

  $c->respond_to(
    json => sub {
      $supporting_data->{errors}            = \%errors;
      $supporting_data->{conversion_errors} = $st_errors;
      $supporting_data->{status_counts}     = $status_counts;
      $c->render( json => $supporting_data );
    },
    html => sub {
      $c->stash(%$supporting_data);
      $c->render(
        template          => 'convert',
        errors            => \%errors,
        conversion_errors => $st_errors,
        status_counts     => $status_counts,
      );
    },
  );
}

sub validation_form_errors {
  my ( $c, $form_validation ) = @_;

  my $supporting_data = validation_supporting_data();

  $c->respond_to(
    json => sub {
      my %errors =
        map { $_ => $form_validation->error($_) }
        grep { $form_validation->has_error($_) }
        qw(metadata_file file_format rule_set_name);
      $supporting_data->{errors} = \%errors;
      $c->render( json => $supporting_data );
    },
    html => sub {
      $c->stash(%$supporting_data);
      $c->render( template => 'validate' );
    },
  );
}

sub move_to_tmp {
  my ( $metadata_file, $loader ) = @_;
  my $tmp_upload_dir  = File::Temp->newdir();
  my $tmp_upload_path = $tmp_upload_dir->dirname . '/uploaded_file';

  $metadata_file->move_to($tmp_upload_path);

  # return the directory object, it will be deleted from the disk
  # when it goes out of scope
  return ( $tmp_upload_dir, $tmp_upload_path );
}

sub load_metadata {
  my ( $metadata_file, $loader ) = @_;

  my ( $tmp_upload_dir, $tmp_upload_path ) = move_to_tmp($metadata_file);

  return $loader->load($tmp_upload_path);
}

sub sampletab_conversion {
  my ( $c, $st_converter, $rule_set ) = @_;

  my $rule_set_name = $c->param('rule_set_name');
  my $metadata_file = $c->param('metadata_file');

  my $validator =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

  my (
    $entity_status,      $entity_outcomes, $attribute_status,
    $attribute_outcomes, $entity_rule_groups,
  ) = $validator->check_all( $st_converter->scd );
  my $reporter = Bio::Metadata::Reporter::BasicReporter->new();

  $c->respond_to(
    json => sub {
      $c->render(
        json => $reporter->report(
          sampletab => join( "\n",
            $st_converter->report_msi, '', $st_converter->report_scd )
        )
      );
    },
    html => sub {
      my $tmp_file = File::Temp->new();

      my $reporter =
        Bio::Metadata::Reporter::ExcelReporter->new(
        file_path => $tmp_file->filename );

      print $tmp_file $st_converter->report_msi;
      print $tmp_file $st_converter->report_scd;

      $c->render_file(
        filepath     => $tmp_file->filename,
        filename     => $metadata_file->filename() . '.sampletab.tsv',
        content_type => $tsv_mime_type,
        cleanup      => 1,
      );
    }
  );

}

sub validate_metadata {
  my ( $c, $metadata, $rule_set ) = @_;

  my $rule_set_name = $c->param('rule_set_name');
  my $metadata_file = $c->param('metadata_file');

  my $validator = $validators->{$rule_set_name};

  my (
    $entity_status,      $entity_outcomes, $attribute_status,
    $attribute_outcomes, $entity_rule_groups,
  ) = $validator->check_all($metadata);
  my $reporter = Bio::Metadata::Reporter::BasicReporter->new();

  $c->respond_to(
    json => sub {

      $c->render(
        json => $reporter->report(
          entities           => $metadata,
          entity_status      => $entity_status,
          entity_outcomes    => $entity_outcomes,
          attribute_status   => $attribute_status,
          attribute_outcomes => $attribute_outcomes
        )
      );
    },
    html => sub {

      my %summary;
      my $total = scalar(@$metadata);
      map { $summary{$_} = 0 } qw(pass error warning);
      map { $summary{$_}++ } values %$entity_status;

      my $attribute_columns =
        $reporter->determine_attr_columns( $metadata, $rule_set );

      my %useage_warning_summary;
      for my $ac (@$attribute_columns) {
        for my $k ( keys %{ $ac->probable_duplicates } ) {
          if ( scalar %{ $ac->probable_duplicates->{$k} } ) {
            $useage_warning_summary{$k}++;
          }
        }
      }

      my %stash = (
        filename               => $metadata_file->filename(),
        outcome_summary        => \%summary,
        total                  => $total,
        rule_set_name          => $rule_set_name,
        rule_set               => $rule_set,
        entities               => $metadata,
        entity_status          => $entity_status,
        entity_outcomes        => $entity_outcomes,
        attribute_status       => $attribute_status,
        attribute_outcomes     => $attribute_outcomes,
        attribute_columns      => $attribute_columns,
        entity_rule_groups     => $entity_rule_groups,
        useage_warning_summary => \%useage_warning_summary,
      );

      $c->stash(%stash);
      $c->render( template => 'validation_output' );

    },
    xlsx => sub {
      my $tmp_file = File::Temp->new();

      my $reporter =
        Bio::Metadata::Reporter::ExcelReporter->new(
        file_path => $tmp_file->filename );

      $reporter->report(
        entities           => $metadata,
        entity_status      => $entity_status,
        entity_outcomes    => $entity_outcomes,
        attribute_status   => $attribute_status,
        attribute_outcomes => $attribute_outcomes,
        rule_set           => $rule_set,
      );

      $c->render_file(
        filepath     => $tmp_file->filename,
        filename     => $metadata_file->filename() . '.validation_report.xlsx',
        content_type => $xlsx_mime_type,
        cleanup      => 1,
      );
    },
    txt => sub {
      my $tmp_file = File::Temp->new();

      my $reporter =
        Bio::Metadata::Reporter::TextReporter->new(
        file_path => $tmp_file->filename );

      $reporter->report(
        entities           => $metadata,
        entity_status      => $entity_status,
        entity_outcomes    => $entity_outcomes,
        attribute_status   => $attribute_status,
        attribute_outcomes => $attribute_outcomes,

      );

      $c->render_file(
        filepath     => $tmp_file->filename,
        filename     => $metadata_file->filename() . '.validation_report.txt',
        content_type => $xlsx_mime_type,
        cleanup      => 1,
      );
    }
  );
}
