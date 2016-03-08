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
use Bio::Metadata::Validate::EntityValidator;
use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Bio::Metadata::BioSample::SampleTab;

plugin 'Config';
plugin 'RenderFile';

my $xlsx_mime_type =
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
my $tsv_mime_type = ' text/tab-separated-values';
app->secrets( ['nosecrets'] );
app->types->type( xlsx => $xlsx_mime_type, tsv => $tsv_mime_type );

my $rule_locations = app->config('rules');
my $loaders        = {
  json           => Bio::Metadata::Loader::JSONEntityLoader->new(),
  biosample_xlsx => Bio::Metadata::Loader::XLSXBioSampleLoader->new()
};

get '/' => sub {
  my $c = shift;
  $c->render( template => 'index' );
};

get '/rule_sets' => sub {
  my $c = shift;

  my $rules = load_rules($rule_locations);

  $c->respond_to(
    json => sub {
      $c->render( json => { rule_set_names => [ sort keys %$rules ] } );
    },
    html => sub {
      $c->stash( rule_sets => $rules );
      $c->render( template => 'rule_sets' );
    }
  );
};

get '/rule_sets/#name' => sub {
  my $c    = shift;
  my $name = $c->param('name');

  my $rule_set = load_rules( $rule_locations, $name );

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

get '/sample_tab' => sub {
  my $c = shift;
  my $supporting_data =
    { valid_rule_set_names => [ sort keys %$rule_locations ], };

  $c->respond_to(
    json => sub {
      $c->render( json => $supporting_data );
    },
    html => sub {
      $c->stash(%$supporting_data);
      $c->render(
        template          => 'sample_tab',
        conversion_errors => [],
        status_counts     => {}
      );
    }
  );
};

post '/sample_tab' => sub {
  my $c = shift;

  my $form_validation = $c->validation;
  form_validate_rule_name($form_validation);
  form_validate_metadata_file($form_validation);

  my $rule_set_name = $c->param('rule_set_name');
  my $metadata_file = $c->param('metadata_file');
  my $rule_set      = load_rules( $rule_locations, $rule_set_name );

  my $st_converter = Bio::Metadata::BioSample::SampleTab->new();
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
  my $validator =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

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
  my $rule_set      = load_rules( $rule_locations, $rule_set_name );

  my $metadata;
  if ( !$form_validation->has_error ) {
    try {
      $metadata = load_metadata( $metadata_file, $loader );
    }
    catch {
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
  $form_validation->required('rule_set_name')->in( keys %$rule_locations );
}

sub load_rules {
  my ( $rule_locations, $name ) = @_;

  my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();

  my @locs = defined $name ? ($name) : keys %$rule_locations;

  my %rules;

  for my $k ( keys %$rule_locations ) {
    my $loc = $rule_locations->{$k};

    if ( !-e $loc && -e "$Bin/$loc" ) {
      $loc = "$Bin/$loc";
    }

    my $rule_set = $loader->load($loc);
    $rules{$k} = $rule_set;
  }

  return defined $name ? $rules{$name} : \%rules;
}

sub validation_supporting_data {
  return {
    valid_file_formats   => [ sort keys %$loaders ],
    valid_rule_set_names => [ sort keys %$rule_locations ],
    valid_output_formats => [qw(html xlsx json)],
  };
}

sub sampletab_form_errors {
  my ( $c, $form_validation, $st_errors, $status_counts ) = @_;

  my $supporting_data =
    { valid_rule_set_names => [ sort keys %$rule_locations ], };

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
        template          => 'sample_tab',
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

  my $validator =
    Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

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

      my $attribute_columns = $reporter->determine_attr_columns($metadata),

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

      );

      $c->render_file(
        filepath     => $tmp_file->filename,
        filename     => $metadata_file->filename() . '.validation_report.xlsx',
        content_type => $xlsx_mime_type,
        cleanup      => 1,
      );
    }
  );
}

__DATA__
@@ layouts/layout.html.ep
<!DOCTYPE html>
<html>
<head>
<title>Validate metadata - <%= $title %></title>
<link href="../favicon.ico" rel="icon" type="image/x-icon" />
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
<style>
  .field-with-error { background-color: rgb(217, 83, 79) }
</style>

</head>
<body>
<div class="container-fluid">
<%= content %>
</div>
<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
<script>
$(document).ready(function(){
  $(function(){
    $('[data-toggle="popover"]').popover({
      html: true,
      content: function () {
        return $(this).next('.popover-content').html();
      }
    })
  })
});
</script>
</body>
</html>

@@ index.html.ep
% layout 'layout', title => 'home';
<h1>Validate metadata REST API</h1>
<h2>Endpoints</h2>
<dl class="dl-horizontal">
<dt>
<a href="./rule_sets">/rule_sets</a>
</dt>
<dd>List rule sets loaded</dd>
<dt>/rule_sets/:name</dt>
<dd>View the detail of one ruleset</dt>
<dt>
  <a href="./validate">/validate</a>
</dt>
<dd>Validate metadata against a rule set</dd>
<dt>
  <a href="./sample_tab">/sample_tab</a>
</dt>
<dd>Convert from Excel to SampleTab format, ready for submission to <a href="http://www.ebi.ac.uk/biosamples/">BioSamples@EMBL-EBI</a></dd>
</dl>
<h2>Response types</h2>
<p>Append <code>?format=<var>x</var></code> to the end of your query to control the format.</p>
<p>Formats available:</p>
<ul>
<li>json</li>
<li>html</li>
</ul>
<p>Alternatively, use the <a href="http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html">"Accept"</a> header in your HTTP request.</p>

@@ rule_sets.html.ep
% layout 'layout', title => 'rule sets';
<h1>Available rule sets</h1>
<p>
<%= scalar(keys %$rule_sets)%> rule sets loaded.
</p>
<dl class="dl-horizontal">
% for my $rule_set_key (sort keys %$rule_sets) {
  <dt>
    <a href="./rule_sets/<%= $rule_set_key %>"><%= $rule_set_key %></a>
  </dt>
  <dd><%= $rule_sets->{$rule_set_key}->name %></dd>
  <dd><%= $rule_sets->{$rule_set_key}->description %></dd>
% }
</dl>

@@ rule_set.html.ep
% layout 'layout', title => $rule_set->name;
<h1><%= $rule_set->name%></h1>
<p class="description"><%= $rule_set->description%></p>
<h2>Rule groups</h2>
% for my $rule_group ($rule_set->all_rule_groups) {
  <h3><%= $rule_group->name %></h3>
  <p class="description"><%= $rule_group->description%></p>

  % if ($rule_group->condition) {
  %  my $condition = $rule_group->condition;
    <p>Applied under these conditions:</p>
    <dl class="dl-horizontal">

    % if ($condition->dpath_condition) {
      <dt>Dpath rule</dt>
      <dd><%= $condition->dpath_condition %></dd>
    % }

    % for my $attr (sort $condition->attribute_value_match_keys) {
    %  my $values = $condition->get_attribute_value_match($attr);

      <dt><%= $attr %></dt>
      <dd>
      % if (scalar(@$values) == 1) {
        is '<%= $values->[0]%>'
      % } else {
        is one of
        <ul class="list-unstyled">
        % for my $val (@$values) {
          <li>'<%= $val%>'</li>
        % }
        </ul>

      % }

      </dd>
    % }

    </dl>
  % } else {
    <p>Applied to all entities</p>
  % }

  <table class="table table-hover table-condensed table-striped">
  <thead><tr>
    <th>Name</th>
    <th>Type</th>
    <th>Required?</th>
    <th>Allow multiple?</th>
    <th>Valid values</th>
    <th>Valid units</th>
    <th>Valid ancestor URIs</th>
  </tr></thead>
  <tbody>
  % for my $rule ($rule_group->all_rules) {
    <tr>
    <td><%= $rule->name %></td>
    <td><%= $rule->type %></td>
    <td><%= $rule->mandatory %></td>
    <td><%= $rule->allow_multiple ? 'Yes' : 'No' %></td>
    <td><ul class="list-unstyled">
    % for my $value ($rule->all_valid_values) {
      <li>'<%= $value %>'</li>
    %}
    </ul></td>
    <td><ul class="list-unstyled">
    % for my $units ($rule->all_valid_units) {
      <li>'<%= $units %>'</li>
    %}
    </ul></td>
    <td><ul class="list-unstyled">
    % for my $uri ($rule->all_valid_ancestor_uris) {
      <li>
        <a href="<%= url_for('http://www.ebi.ac.uk/ols/beta/search')->query({q => $uri}) %>">
          <%= $uri %>
        </a>
      </li>
    %}
    </ul></td>
    </tr>
  %}
  </tbody>
  </table>

% }
</dl>

@@ sample_tab.html.ep
% layout 'layout', title => 'Excel to SampleTab conversion tool';
%= form_for sample_tab => (enctype => 'multipart/form-data', method => 'POST') => begin

<h1>Excel to SampleTab conversion</h1>
<p>Convert an Excel file, based on the sample template, to SampleTab, ready for submission to <a href="http://www.ebi.ac.uk/biosamples">BioSamples@EMBL-EBI</a>.</p>
<dl class="dl-horizontal">
  <dt>
    %= label_for metadata_file => 'Metadata file'
  </dt>
  <dd>
    %= file_field 'metadata_file'
  </dd>
  <dt>
   %= label_for rule_set_name => 'Rule set'
  </dt>
  <dd>
    %= select_field rule_set_name => $valid_rule_set_names
  </dd>
</dl>
%= submit_button 'Convert', class => 'btn btn-primary'
% if ($status_counts && %$status_counts){
  <h2>Validation outcome summary</h2>
  <p>The following list shows how many of the entities (e.g. samples) submitted hit each validation status.
  You can get more detail from the
  %= link_to 'validation' => 'validate'
  page
</p>
  <dl class="dl-horizontal">
% for my $k (sort keys %$status_counts) {
  <dt>
    %= $k
  </dt>
  <dd>
    %= $status_counts->{$k}
  </dd>
% }
  </dl>


% }
% if ($conversion_errors && @$conversion_errors) {
<h2>SampleTab Conversion errors</h2>
<table class="table table-hover table-striped table-condensed">
  <thead>
    <tr>
      <th>Item</th>
      <th>Status</th>
      <th>Message</th>
    </tr>
  </thead>
% for my $outcome (@$conversion_errors) {
  <tr>
    <td>
%= $outcome->rule ? $outcome->rule->name : $outcome->get_attribute(0) ? $outcome->get_attribute(0)->name : ''
    </td>
    <td>
%= $outcome->outcome
    </td>
    <td>
%= $outcome->message
    </td>
  </tr>
% }
</table>
% }
% end

@@ validate.html.ep
% layout 'layout', title => 'validation tool';
%= form_for validate => (enctype => 'multipart/form-data', method => 'POST') => begin

<h1>Metadata validation</h1>
<dl class="dl-horizontal">

  <dt>
    %= label_for metadata_file => 'Metadata file'
  </dt>
  <dd>
    %= file_field 'metadata_file'
  </dd>

  <dt>
   %= label_for file_format => 'File format'
  </dt>
  <dd>
    %= select_field file_format => $valid_file_formats
  </dd>

  <dt>
   %= label_for rule_set_name => 'Rule set'
  </dt>
  <dd>
    %= select_field rule_set_name => $valid_rule_set_names
  </dd>

  <dt>
   %= label_for format => 'output format'
  </dt>
  <dd>
    %= select_field format => $valid_output_formats
  </dd>

</dl>
%= submit_button 'Validate', class => 'btn btn-primary'
% end

@@ validation_output.html.ep
% layout 'layout', title => 'validation summary';
<h1>Validation result</h1>

<div>
% my @categories = qw(value units ref_id uri);
  <!-- Nav tabs -->
  <ul class="nav nav-tabs" role="tablist">

  <li role="presentation" class="active">
    <a href="#summary" aria-controls="profile" role="tab" data-toggle="tab">Summary</a>
  </li>

  <li role="presentation">
    <a href="#entities" aria-controls="profile" role="tab" data-toggle="tab">Entities</a>
  </li>

% for my $cat (@categories){
  <li role="presentation">
    <a href="#useage-<%= $cat %>" aria-controls="profile" role="tab" data-toggle="tab">Useage - <%= $cat %></a>
  </li>
% }
  </ul>

  <!-- Tab panes -->
  <div class="tab-content">

  <div role="tabpanel" class="tab-pane active" id="summary">
    <br/>
    % if ($outcome_summary->{error}) {
      <div class="alert alert-danger" role="alert">
        <strong>Oh dear.</strong> The metadata did not pass validation. Please review the errors in the 'Entities' tab and update your metadata.
      </div>
    % } elsif ($outcome_summary->{warning}) {
      <div class="alert alert-warning" role="alert">
        <strong>Not bad.</strong> The metadata passed validation, but with some warnings. Please review the errors in the 'Entities' tab and consider updating your metadata.
      </div>
    % } elsif ($outcome_summary->{pass}) {
      <div class="alert  alert-pass" role="alert">
        <strong>Well done.</strong> The metadata passed validation.
      </div>
    %}

    <br/>

    % if (scalar(%$useage_warning_summary)) {
      <div class="alert alert-warning" role="alert">
        Some of the terms used look like they might have slight differences, such as different capitalisation or punctuation. This can make two entities look more different than they really are. Please check these useage tabs for problems:
        <ul>
        % for my $cat (sort keys %$useage_warning_summary){
          <li>Usage - <%= $cat%></li>
        %}
        </ul>
      </div>
    % }

    <p><%= $total %></dd> entities from <b><%= $filename %></b> were validated against the <%= link_to $rule_set_name => 'rule_sets/'.$rule_set_name %> rule set, with the following outcomes:</p>

    <dl class="dl-horizontal">

      % for my $o (sort keys %$outcome_summary){
      <dt><%= $o %></dt>
      <dd><%= $outcome_summary->{$o} %></dd>
      %}
    </dl>

    <p>This report is also available as a spreadsheet, just go back and submit the metadata and choose 'xlsx' as the output format.</p>

  </div>

  <div role="tabpanel" class="tab-pane" id="entities">
    <table class="table table-hover table-condensed table-striped">

      <thead>
        <th>
          ID
        </th>
        <th>
          Status
        </th>
        <th>
          Entity type
        </th>
        <th>Rule groups applied</th>

    % for my $col (@{$attribute_columns}){
    %   for my $i (0..($col->max_count - 1)) {
          <th><%= $col->name %></th>
    %     if ($col->use_ref_id){
            <th>Term source REF</th>
            <th>Term source ID</th>
    %     }
    %     if ($col->use_uri){
            <th>URI</th>
    %     }
    %     if ($col->use_units){
            <th>Units</th>
    %     }
    %   }
    % }
      </thead>
      <tbody>

    % my %class_lookup =(pass => 'success', warning => 'warning',error   => 'danger',);

    % for my $ent (@{$entities}) {
    % my $ent_status = $entity_status->{$ent};
    % my $ent_outcomes = $entity_outcomes->{$ent};
      <tr>
        <td><%= $ent->id %></td>
        <td>
    %     my $btn_class = $class_lookup{$ent_status};

          <button type="button" class="btn btn-<%= $btn_class %>" data-container="body" data-toggle="popover" data-placement="right" data-title="Notes" data-trigger="focus">
            <%= $ent_status %>
          </button>
          <div class="hidden popover-content">
          <ul class="outcomes">
    %       for my $o (@$ent_outcomes) {
              <li class="bg-<%= $class_lookup{$o->outcome} %>">
                <%= $o->message %>
    %            if ($o->rule) {
                 (<b><%= $o->rule->name %></b> from the <b><%= $o->rule_group->name %></b> rule group)
    %           }else{
                 (<b><%= $o->get_attribute(0)->name %></b>)
    %           }
              </li>
    %       }
    %     if (!scalar(@$ent_outcomes)){
            <li class="bg-success">No problems found</li>
    %     }
          </ul>
          <div>

        </td>
        <td><%= $ent->entity_type %></td>
        <td>
          <ul>
    % for my $rg (@{$entity_rule_groups->{$ent}}){
              <li><%= $rg->name %></li>
    % }
          </ul>
        </td>

    % my $organised_attr = $ent->organised_attr;

    % for my $col (@{$attribute_columns}){
    % my $attrs = $organised_attr->{ $col->name };
    %   for my $i (0..($col->max_count - 1)) {
    %     my ($a,$a_status,$a_outcomes) = (undef,'',[]);
    %     if ( $attrs && $i < scalar(@$attrs) && $attrs->[$i] ) {
    %         $a = $attrs->[$i];
    %     }
    %     if ($a) { $a_status = $attribute_status->{$a};$a_outcomes = $attribute_outcomes->{$a}};
          <td>
          <%= $a ? $a->value : '' %>
    %     if (defined $a_outcomes && scalar(@$a_outcomes)){
            <button type="button" class="btn btn-<%= $class_lookup{$a_status} %>" data-container="body" data-toggle="popover" data-placement="right" data-title="Notes" data-trigger="focus">
              <%= $a_status %>
            </button>
            <div class="hidden popover-content">
            <ul class="outcomes">
    %         for my $o (@$a_outcomes) {
                <li class="bg-<%= $class_lookup{$o->outcome} %>">
                  <%= $o->message %>
    %             if ($o->rule) {
                   (<b><%= $o->rule_group->name %></b> rule group)
    %             }
                </li>
    %         }
    %       if (!scalar(@$a_outcomes)){
              <li class="bg-success">No problems found</li>
    %       }
            </div>
    %     }

          </td>
    %     if ($col->use_ref_id){
            <td><%= $a ? $a->source_ref : '' %></td>
            <td><%= $a ? $a->id : '' %></td>
    %     }
    %     if ($col->use_uri){
            <td><%= $a ? $a->uri : '' %></td>
    %     }
    %     if ($col->use_units){
            <td><%= $a ? $a->units : '' %></td>
    %     }
    %   }
    % }

      </tr>
    % }
      </tbody>
    </table>
  </div>


  %for my $cat (@categories){
    <div role="tabpanel" class="tab-pane" id="useage-<%= $cat %>">
      <table class="table table-hover table-condensed table-striped">
        <th>Attribute</th>
        <th><%= $cat %></th>
        <th>count</th>
        <thead>
      </thead>
      <tbody>
        % for my $col (@$attribute_columns){
        % my $loop_count = 0;
        % my $term_count = $col->term_count->{$cat};
        %  for my $term  (sort keys %$term_count){
        %  my $cell_class = ($col->probable_duplicates()->{$cat}{$term}) ? 'bg-danger' : '';
            <tr>
              <td><%= ($loop_count++) ? '' : $col->name %></td>
              <td class="<%= $cell_class%>"><%= $term %></td>
              <td><%= $term_count->{$term} %></td>
            </tr>
        %  }
        % }
      </tbody>
      </table>
    </div>
  % }
  </div>

</div>



@@ not_found.html.ep
% layout 'layout', title => 'not found';
<h1>404 - not found</h1>
<p>Sorry, but the content you requested cannot be found. Please tell us so we can fix it.</p>

@@ exception.html.ep
% layout 'layout', title => 'error';
<h1>Exception</h1>
<pre><%= $exception->message %></pre>
<h1>Stash</h1>
<pre><%= dumper $snapshot %></pre>
