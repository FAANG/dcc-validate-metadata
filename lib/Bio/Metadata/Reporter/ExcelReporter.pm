
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

package Bio::Metadata::Reporter::ExcelReporter;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;
use Excel::Writer::XLSX;
use Bio::Metadata::Reporter::AttributeColumn;
use Data::Dumper;

with "Bio::Metadata::Reporter::ReporterRole";

has 'file_path' => ( is => 'rw', isa => 'Str', required => 1 );
has '_workbook' => ( is => 'rw', isa => 'Excel::Writer::XLSX' );
has 'warning_color' =>
  ( is => 'rw', isa => 'Str', required => 1, default => 'orange' );
has 'error_color' =>
  ( is => 'rw', isa => 'Str', required => 1, default => 'red' );
has 'pass_color' =>
  ( is => 'rw', isa => 'Str', required => 1, default => 'green' );

has '_formats' => (
    is      => 'rw',
    isa     => 'HashRef[Any]',
    traits  => ['Hash'],
    handles => { get_format => 'get', }
);

sub report {
    my ( $self, %params ) = @_;
    my $entities           = $params{entities};
    my $entity_status      = $params{entity_status};
    my $entity_outcomes    = $params{entity_outcomes};
    my $attribute_status   = $params{attribute_status};
    my $attribute_outcomes = $params{attribute_outcomes};

    $self->create_workbook();
    $self->create_formats();

    my $attr_columns = $self->determine_attr_columns($entities);

    #create entities report
    my $entity_sheet = $self->new_worksheet("entities");

    $self->write_header( $entity_sheet, $attr_columns );
    $self->write_entities( $entity_sheet, $attr_columns, $entities,
        $entity_status, $entity_outcomes, $attribute_status,
        $attribute_outcomes );

    my $col            = 1;
    my $rborder_format = $self->get_format('rborder');
    $entity_sheet->set_column( 0, $col, 15, $rborder_format );

    for my $ac (@$attr_columns) {
        my $col_to_cover_per_attr = 1;
        $col_to_cover_per_attr++ if ( $ac->use_units );
        $col_to_cover_per_attr++ if ( $ac->use_uri );
        #$col_to_cover_per_attr =+ 2 if ( $ac->use_ref_id );
        
        $col = $col + ( $ac->max_count * $col_to_cover_per_attr );

        $entity_sheet->set_column( $col, $col, undef, $rborder_format );
    }

    #create term usage reports
    my $values_sheet = $self->new_worksheet("values");
    $self->report_uniq_usage( $values_sheet, 'value', $attr_columns );

    my $units_sheet = $self->new_worksheet("units");
    $self->report_uniq_usage( $units_sheet, 'units', $attr_columns );

    my $uris_sheet = $self->new_worksheet("uris");
    $self->report_uniq_usage( $uris_sheet, 'uri', $attr_columns );
    
    my $refid_sheet = $self->new_worksheet("ref+id");
    $self->report_uniq_usage( $refid_sheet, 'ref_id', $attr_columns );

}

sub report_uniq_usage {
    my ( $self, $sheet, $key, $attr_columns ) = @_;

    my $hformat = $self->get_format('header');
    my $wformat = $self->get_format('warning');

    my $row = 0;

    $sheet->write( $row, 0, "attribute", $hformat );
    $sheet->write( $row, 1, $key,        $hformat );
    $sheet->write( $row, 2, "count",     $hformat );

    $row++;

  AC: for my $ac (@$attr_columns) {
        my $term_count          = $ac->term_count->{$key};
        my $probable_duplicates = $ac->probable_duplicates->{$key};

        if ( !keys %$term_count ) {

            #attribute column doesn't have any terms of this type, don't report
            next AC;
        }

        $sheet->write( $row, 0, $ac->name );

        for my $k ( sort { lc($a) cmp lc($b) } keys %$term_count ) {
            $sheet->write( $row, 1, $k, );

            if ( $probable_duplicates->{$k} ) {
                $sheet->write( $row, 1, $k, $wformat );
            }
            else {
                $sheet->write( $row, 1, $k );
            }
            $sheet->write( $row, 2, $term_count->{$k} );

            $row++;
        }

    }

    my $rborder_format = $self->get_format('rborder');
    $sheet->set_column( 0, 1, 15, $rborder_format );

}

sub create_formats {
    my ( $self, ) = @_;

    my $workbook = $self->_workbook;

    my %format;
    $format{'pass'}    = $workbook->add_format();
    $format{'warning'} = $workbook->add_format();
    $format{'error'}   = $workbook->add_format();
    $format{'header'}  = $workbook->add_format();
    $format{'rborder'} = $workbook->add_format();

    $format{'pass'}->set_bg_color( $self->pass_color );
    $format{'warning'}->set_bg_color( $self->warning_color );
    $format{'error'}->set_bg_color( $self->error_color );

    $format{'header'}->set_bold();
    $format{'header'}->set_bottom();

    $format{'rborder'}->set_right();

    $self->_formats( \%format );
}

sub prep_attr_comment {
    my ( $self, $attr_outcomes ) = @_;

    my $comment = '';

    if ( $attr_outcomes && @$attr_outcomes ) {
        $comment .= join "\n", map { $_->message } @$attr_outcomes;
        $comment .= "\n";
    }

    return $comment;
}

sub prep_entity_comment {
    my ( $self, $entity_outcomes ) = @_;

    my @general_outcomes = grep { @{ $_->attributes } == 0 } @$entity_outcomes;

    my $comment = '';
    if (@general_outcomes) {
        $comment .= join "\n",
          map { $_->rule->name . ': ' . $_->message } @general_outcomes;
        $comment .= "\n";
    }

    if ( scalar(@$entity_outcomes) > scalar(@general_outcomes) ) {
        my $extras_count =
          scalar(@$entity_outcomes) - scalar(@general_outcomes);
        $comment .= "$extras_count attribute notes";
    }
    return $comment;
}

sub write_entities {
    my ( $self, $worksheet, $attr_columns, $entities, $entity_status,
        $entity_outcomes, $attribute_status, $attribute_outcomes )
      = @_;

    my $row = 0;

    for my $e (@$entities) {
        $row++;
        my $col = 0;

        my $entity_format = $self->get_format( $entity_status->{$e} );

        $worksheet->write( $row, $col, $e->id, $entity_format );
        my $entity_comment =
          $self->prep_entity_comment( $entity_outcomes->{$e} );
        if ($entity_comment) {
            $worksheet->write_comment( $row, $col, $entity_comment );
        }
        $col++;

        $worksheet->write( $row, $col++, $e->entity_type );

        my $organised_attr = $e->organised_attr;

        for my $ac (@$attr_columns) {
            my $attrs = $organised_attr->{ $ac->name };
            for ( my $i = 0 ; $i < $ac->max_count ; $i++ ) {
                my $a;
                if ( $attrs && $i < scalar(@$attrs) && $attrs->[$i] ) {
                    $a = $attrs->[$i];
                }

                if ($a) {
                    my $as = $attribute_status->{$a};

                    if ( $as && $self->get_format($as) ) {
                        $worksheet->write( $row, $col, $a->value,
                            $self->get_format($as) );
                    }
                    else {
                        $worksheet->write( $row, $col, $a->value );
                    }

                    my $attr_comment =
                      $self->prep_attr_comment( $attribute_outcomes->{$a} );
                    if ($attr_comment) {
                        $worksheet->write_comment( $row, $col, $attr_comment );
                    }

                }
                $col++;

                if ( $ac->use_units ) {
                    if ( $a && $a->units ) {
                        $worksheet->write( $row, $col, $a->units );
                    }

                    $col++;
                }

                if ( $ac->use_uri ) {
                    if ( $a && $a->uri ) {
                        $worksheet->write( $row, $col, $a->uri );
                    }

                    $col++;
                }
            }
        }
    }

}

sub write_header {
    my ( $self, $worksheet, $attr_columns ) = @_;

    my $row = 0;
    my $col = 0;

    my $format = $self->get_format('header');

    $worksheet->write( $row, $col++, 'ID',          $format );
    $worksheet->write( $row, $col++, 'entity_type', $format );

    for my $ac (@$attr_columns) {
        for ( my $i = 0 ; $i < $ac->max_count ; $i++ ) {
            $worksheet->write( $row, $col++, $ac->name, $format );
            if ( $ac->use_units ) {
                $worksheet->write( $row, $col++, 'units', $format );
            }
            if ( $ac->use_uri ) {
                $worksheet->write( $row, $col++, 'URI', $format );
            }
        }
    }
}

sub create_workbook {
    my ($self) = @_;
    my $workbook = Excel::Writer::XLSX->new( $self->file_path );
    croak "Could not create Excel file: $!" unless ( defined $workbook );
    $self->_workbook($workbook);
}

sub new_worksheet {
    my ( $self, $sheet_name ) = @_;
    return $self->_workbook()->add_worksheet($sheet_name);
}

__PACKAGE__->meta->make_immutable;

1;
