package Bio::Metadata::Loader::XLSXLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use Data::Dumper;
use Spreadsheet::ParseXLSX;

requires 'process_sheet';

sub load {
    my ( $self, $file_path, $sheet_names ) = @_;

    my %to_process = map { $_ => 1 } @$sheet_names;

    my @entities;

    my $parser = Spreadsheet::ParseXLSX->new;
    my $workbook = $parser->parse($file_path);

    for my $sheet  ($workbook->worksheets ) {
        my $set;
        if (%to_process) {
            next unless exists( $to_process{ $sheet->get_name } );
            $set = $self->process_sheet($sheet);
        }
        else {
            $set = $self->process_sheet($sheet);
        }
        if ( $set != 0 ) {
            foreach my $e (@$set) {
                push @entities, $e;
            }
        }
    }
    print "[WARNING] No entities retrieved from $file_path" if !@entities;
    return \@entities;
}

sub expand {
    my ( $self, $file_path, $sheet_names, $entities ) = @_;
    
    my %to_process = map { $_ => 1 } @$sheet_names;

    my $parser = Spreadsheet::ParseXLSX->new;
    my $workbook = $parser->parse($file_path);

    for my $sheet  ($workbook->worksheets ) {
        if (%to_process) {
            next unless exists( $to_process{ $sheet->get_name } );
            $entities = $self->process_expansion_sheet($sheet, $entities);
        }
        else {
            $entities = $self->process_expansion_sheet($sheet, $entities);
        }
    }

    return $entities;
}

1;
