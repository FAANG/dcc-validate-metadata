package Bio::Metadata::Loader::XLSXLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use Spreadsheet::ParseExcel::Stream::XLSX;

requires 'process_sheet';

sub load {
	my ( $self, $file_path ) = @_;
	
	my @entities;
	
	my $xls = Spreadsheet::ParseExcel::Stream::XLSX->new($file_path);

	while ( my $sheet = $xls->sheet() ) {
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
