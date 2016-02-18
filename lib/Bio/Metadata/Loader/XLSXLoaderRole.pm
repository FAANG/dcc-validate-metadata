package Bio::Metadata::Loader::XLSXLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use Spreadsheet::ParseExcel::Stream::XLSX;
use List::Util qw(any);
requires 'process_sheet';

sub load {
	my ( $self, $file_path, $sheet_names ) = @_;
	
	my @entities;
	
	my $xls = Spreadsheet::ParseExcel::Stream::XLSX->new($file_path);


	while ( my $sheet = $xls->sheet() ) {
    if ($sheet_names){
      my $match = any {$sheet->name eq $_} @$sheet_names;
      next if(!$match);
    }
    
    
	 	my $set=$self->process_sheet($sheet);
		if ($set!=0) {
			foreach my $e (@$set) {
				push @entities,$e
			}
		}
	}
	
	return \@entities;
}

1;
