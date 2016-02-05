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
use Mojolicious::Lite;
use Carp;
use File::Temp qw(tempfile);

use Bio::Metadata::Loader::JSONRuleSetLoader;
use Bio::Metadata::Loader::JSONEntityLoader;
use Bio::Metadata::Reporter::ExcelReporter;
use Bio::Metadata::Reporter::JsonReporter;
use Bio::Metadata::Validate::EntityValidator;
use UUID::Generator::PurePerl;

plugin 'Config';
plugin 'RenderFile';

app->secrets( ['nosecrets'] );

my $rule_locations = app->config('rules');
my $rules          = load_rules($rule_locations);
my $loaders        = { json => Bio::Metadata::Loader::JSONEntityLoader->new() };

my $uuid_generator = UUID::Generator::PurePerl->new();
my %report_files;

get '/' => sub {
    my $c   = shift;
    my $url = $c->req->url->to_abs->to_string;
    $url =~ s/\/$//;
    $c->render( template => 'index', title => '', url => $url );
};

get '/rule_sets' => sub {
    my $c = shift;

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
    my $c        = shift;
    my $name     = $c->param('name');
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
    $form_validation->required('rule_set_name')->in( keys %$rules );
    $form_validation->required('file_format')->in( keys %$loaders );
    $form_validation->required('metadata_file')
      ->upload->size( 1, 16 * ( 10**6 ) );

    if ( $form_validation->has_error ) {
        validation_form_errors( $c, $form_validation );
    }
    else {
        validate_metadata($c);
    }
};

get '/validation_summary' => sub {
    my $c = shift;

    $c->stash(
        total           => $c->flash("total"),
        outcome_summary => $c->flash("outcome_summary"),
        report          => $c->flash("report")
    );

    $c->render( template => 'validation_summary' );
};

get '/report/#report' => sub {
    my $c = shift;

    my $key = $c->param('report');
    my $report = delete $report_files{$key};

    $c->render_file(
        filepath => $report->{tmp_file}->filename,
        filename => $report->{report_filename},
        content_type =>
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        content_disposition => 'attachment',
        cleanup             => 1,
    );
};

# Start the Mojolicious command system
app->start;

sub load_rules {
    my ($rule_locations) = @_;

    my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();
    my %rules;

    for my $k ( keys %$rule_locations ) {
        my $loc      = $rule_locations->{$k};
        my $rule_set = $loader->load($loc);
        $rules{$k} = $rule_set;
    }

    return \%rules;
}

sub validation_supporting_data {
    return {
        valid_file_formats   => [ sort keys %$loaders ],
        valid_rule_set_names => [ sort keys %$rules ],
    };
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
        }
    );
}

sub validate_metadata {
    my ( $c, $target ) = @_;

    my $metadata_file = $c->param('metadata_file');
    my $loader        = $loaders->{ $c->param('file_format') };
    my $rule_set      = $rules->{ $c->param('rule_set_name') };

    my $metadata =
      $loader->load_blob( $metadata_file->slurp, $metadata_file->filename );

    my $validator =
      Bio::Metadata::Validate::EntityValidator->new( rule_set => $rule_set );

    my (
        $entity_status,    $entity_outcomes,
        $attribute_status, $attribute_outcomes
    ) = $validator->check_all($metadata);

    $c->respond_to(
        json => sub {
            my $reporter = Bio::Metadata::Reporter::JsonReporter->new();
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
            my $tmp_file = File::Temp->new();
            my $key      = $uuid_generator->generate_v1()->as_string();

            my ( $tmpfh, $report_filepath ) = tempfile();

            my $reporter =
              Bio::Metadata::Reporter::ExcelReporter->new(
                file_path => $tmp_file->filename );

            $reporter->report(
                entities           => $metadata,
                entity_status      => $entity_status,
                entity_outcomes    => $entity_outcomes,
                attribute_status   => $attribute_status,
                attribute_outcomes => $attribute_outcomes
            );

            my %summary;
            my $total = scalar(@$metadata);
            map { $summary{$_}++ } values %$entity_status;
            $c->flash(
                outcome_summary => \%summary,
                total           => $total,
                report          => $key
            );

            $report_files{$key} = {
              tmp_file => $tmp_file,
              report_filename => $metadata_file->filename().'.validation_report.xlsx'
            };

            $c->redirect_to('validation_summary');
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
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootswatch/3.3.5/readable/bootstrap.min.css">
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
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
<script>
$(document).ready(function(){
  $("body").on("click",".report_link",function(){
    $(this).click(function () {return false;}).attr("disabled","disabled");
  });
});
</script>
</body>
</html>

@@ index.html.ep
% layout 'layout', title => 'home';
<h1>Validate metadata REST API</h1>
<h2>Endpoints</h2>
<dl class="dl-horizontal">
<dt><a href="<%= $url %>/rule_sets">/rule_sets</a></dt>
<dd>List rule sets loaded</dd>
<dt>/rule_sets/:name</dt>
<dd>View the detail of one ruleset</dt>
<dt><a href="<%= $url %>/validate">/validate</a></dt>
<dd>Validate metadata against a rule set</dd>
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
  <dt><a href="/rule_sets/<%= $rule_set_key %>"><%= $rule_set_key %></a></dt>
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
   %= label_for format => 'test format'
  </dt>
  <dd>
    %= select_field format => ['json', 'html']
  </dd>

</dl>
%= submit_button 'Validate', class => 'btn btn-primary'
% end

@@ validation_summary.html.ep
% layout 'layout', title => 'validation summary';
<h1>Validation summary</h1>
<dl class="dl-horizontal">
  
  % for my $o (sort keys %$outcome_summary){ 
  <dt><%= $o %></dt>
  <dd><%= $outcome_summary->{$o} %></dd>
  %}
  <dt>Total</dt>
  <dd><%= $total %></dd>
</dl>
%= link_to Report => 'report/'.$report => {} => (class => 'btn btn-primary report_link')


@@ not_found.html.ep
% layout 'layout', title => 'not found';
<h1>404 - not found</h1>
<p>Sorry, but the content you requested cannot be found. Please tell us so we can fix it.</p>

@@ exception.html.ep
% layout 'layout', title => 'error';
<h1>Exception</h1>
<p><%= $exception->message %></p>
<h1>Stash</h1>
<pre><%= dumper $snapshot %></pre>
  
