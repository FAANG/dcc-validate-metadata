
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

package Bio::Metadata::Reporter::BasicReporter;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use Bio::Metadata::Types;
use namespace::autoclean;
use JSON::MaybeXS;

with "Bio::Metadata::Reporter::ReporterRole";

has 'pretty_print' => (is => 'rw', isa => 'Bool', default => 1);

sub report {
  my ( $self, %params ) = @_;
  my $entities           = $params{entities};
  my $entity_status      = $params{entity_status};
  my $entity_outcomes    = $params{entity_outcomes};
  my $attribute_status   = $params{attribute_status};
  my $attribute_outcomes = $params{attribute_outcomes};

  my $output = $self->prep_output($entities);

  $self->process_entities( $entities, $output, $entity_status,
    $entity_outcomes, $attribute_status, $attribute_outcomes );
  $self->add_term_usage( $entities, $output );

  my $fh = undef;

  if ($self->file_path && ! $self->file_handle) {
    open $fh, '>', $self->file_path;
    $self->file_handle($fh);
  }

  if ($self->file_handle){
    my $json = JSON->new();

    if ($self->pretty_print){
      $json = $json->pretty;
    }
    my $ofh = $self->file_handle;
    print $ofh $json->encode($output);
  }

  close $fh if ($fh);

  return $output;
}

sub add_term_usage {
  my ( $self, $entities, $output ) = @_;

  my @column_report =
    map { $_->to_hash } ( @{ $self->determine_attr_columns($entities) } );

  for my $ac (@column_report) {
    for my $c ( keys %{ $ac->{probable_duplicates} } ) {
      $ac->{probable_duplicates}{$c} =
        [ sort keys %{ $ac->{probable_duplicates}{$c} } ];
    }
  }

  $output->{column_report} = \@column_report;
}

sub process_entities {
  my ( $self, $entities, $output, $entity_status, $entity_outcomes,
    $attribute_status, $attribute_outcomes )
    = @_;

  for my $e (@$entities) {
    $output->{summary}{ $entity_status->{$e} }++;

    my $ent =
      $self->report_outcome( $e, $entity_status->{$e}, $entity_outcomes->{$e} );
    my @attributes = map {
      $self->report_outcome(
        $_,
        $attribute_status->{$_},
        $attribute_outcomes->{$_}
        )
    } $e->all_attributes;
    $ent->{attributes} = \@attributes;
    push @{ $output->{entities} }, $ent;
  }
}

sub prep_output {
  my ( $self, $entities ) = @_;

  my %output =
    ( entities => [], summary => {}, entity_count => scalar(@$entities), );

  for my $o (@Bio::Metadata::Types::OUTCOME_VALUES) {
    $output{summary}{$o} = 0;
  }
  return \%output;
}

sub report_outcome {
  my ( $self, $entity, $status, $outcomes ) = @_;

  my $e = $entity->to_hash;
  $e->{_outcome} = {
    status => $status || 'pass',
    errors =>
      [ map { $_->message } grep { $_->outcome eq 'error' } @$outcomes ],
    warnings =>
      [ map { $_->message } grep { $_->outcome eq 'warning' } @$outcomes ],
  };

  return $e;
}

__PACKAGE__->meta->make_immutable;

1;
