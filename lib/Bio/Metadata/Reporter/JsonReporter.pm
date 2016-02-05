
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

package Bio::Metadata::Reporter::JsonReporter;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;

with "Bio::Metadata::Reporter::ReporterRole";

sub report {
    my ( $self, %params ) = @_;
    my $entities           = $params{entities};
    my $entity_status      = $params{entity_status};
    my $entity_outcomes    = $params{entity_outcomes};
    my $attribute_status   = $params{attribute_status};
    my $attribute_outcomes = $params{attribute_outcomes};



    my %output = ( entities => [], summary => {total => 0} );

    for my $e (@$entities) {
      
      $output{summary}{total}++;
      $output{summary}{$entity_status->{$e}}++;

      
        my $ent =
          $self->report_outcome( $e, $entity_status->{$e},
            $entity_outcomes->{$e} );
        my @attributes = map {
            $self->report_outcome(
                $_,
                $attribute_status->{$_},
                $attribute_outcomes->{$_}
              )
        } $e->all_attributes;
        $ent->{attributes} = \@attributes;
        push @{ $output{entities} }, $ent;
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
