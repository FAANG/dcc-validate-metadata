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

use Bio::Metadata::Loader::JSONRuleSetLoader;

plugin 'Config';

my $rule_locations = app->config('rules');

my $rules = load_rules($rule_locations);

get '/' => sub {
    my $self = shift;
    my $url  = $self->req->url->to_abs->to_string;
    $url =~ s/\/$//;
    $self->render( template => 'index', title => '', url => $url );
};

get '/rule_sets' => sub {
    my $self = shift;

    $self->respond_to(
        json => sub { $self->render( json => [sort keys %$rules] ) },
        html => sub {
            $self->stash(
                rule_sets => $rules,
                title          => 'rule sets'
            );
            $self->render( template => 'rule_sets' );
        }
    );
};

get '/rule_sets/#name' => sub {
    my $self     = shift;
    my $name     = $self->param('name');
    my $rule_set = $rules->{$name};

    return $self->reply->not_found if (!$rule_set);

    $self->respond_to(
        json => sub {
            $self->render( json => $rule_set->to_hash );
        },
        html => sub {
            $self->stash( rule_set => $rule_set, title => 'rule set ' . $name );
            $self->render( template => 'rule_set' );
        }
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

__DATA__
@@ layouts/layout.html.ep
<!DOCTYPE html>
<html>
<head>
<title>Validate metadata - <%= $title %></title>
<link href="../favicon.ico" rel="icon" type="image/x-icon" />
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootswatch/3.3.5/slate/bootstrap.min.css">
</head>
<body>
<div class="container-fluid">
<%= content %>
</div>
<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
</body>
</html>

@@ index.html.ep
% layout 'layout';
<h1>Validate metadata REST API</h1>
<h2>Endpoints</h2>
<dl class="dl-horizontal">
<dt><a href="<%= $url %>/rule_sets">/rule_sets</a></dt>
<dd>List rule sets loaded</dd>
<dt>/rule_sets/:name</dt>
<dd>View the detail of one ruleset</dt>
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
% layout 'layout';
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
% layout 'layout';
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