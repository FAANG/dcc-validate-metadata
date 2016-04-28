
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

package Bio::Metadata::Reporter::TextReporter;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;
use Bio::Metadata::Reporter::AttributeColumn;
use Data::Dumper;

with "Bio::Metadata::Reporter::ReporterRole";

has 'max_size_msg' => ( is => 'rw', isa => 'Int' );

sub report {
  my ( $self, %params ) = @_;
  my $entities           = $params{entities};
  my $entity_status      = $params{entity_status};
  my $entity_outcomes    = $params{entity_outcomes};
  my $attribute_status   = $params{attribute_status};
  my $attribute_outcomes = $params{attribute_outcomes};

  if (!$self->file_path && !$self->file_handle){
    confess "report called without file_path or file_handle";
  }
  my $close_fh = undef;
  if ($self->file_path && !$self->file_handle){
    $close_fh = 1;
    open my $outfh, ">", $self->file_path;
    $self->file_handle($outfh);
  }

  $self->_print($entity_outcomes);

  if ($close_fh){
    close $self->file_handle;
  }
}

sub _print {
  my ( $self, $entity_outcomes ) = @_;
  my $sep = "\t";

  my $outfh = $self->file_handle;

  print $outfh join( $sep, '#id', 'status', 'message', 'attribute','value','unit','term_source','term_source_id' ) . $/;

  foreach my $e ( keys %$entity_outcomes ) {
    my @outcomes = @{ $entity_outcomes->{$e} };
    foreach my $o (@outcomes) {
      my $msg = $o->message;
      if ( $o->message
        && $self->max_size_msg
        && length($msg) > $self->max_size_msg )
      {
        $msg = substr( $o->message, 0, $self->max_size_msg );
      }

      my $attr = join( $sep, grep {$_} map { $_->name } @{ $o->attributes } );
      $attr = $o->rule->name if (!$attr && $o->rule->name);
      my $val = join( $sep, grep {$_} map { $_->value } @{ $o->attributes } );
      my $src_ref = join( $sep, grep {$_} map { $_->source_ref } @{ $o->attributes } );
      my $term_id = join( $sep, grep {$_} map { $_->id } @{ $o->attributes } );
      my $units = join( $sep, grep {$_} map { $_->units } @{ $o->attributes } );

      if ( $o->outcome eq 'error' ) {
        print $outfh join( $sep, $o->entity->id, $o->outcome, $msg, $attr, $val, $units, $src_ref, $term_id) . $/;
      }
      elsif ( $o->outcome eq 'warning' ) {
        print $outfh
          join( $sep, $o->entity->id, $o->outcome, "'" . $msg . "'", $val )
          . $/;
      }
    }
  }
}

__PACKAGE__->meta->make_immutable;

1;
