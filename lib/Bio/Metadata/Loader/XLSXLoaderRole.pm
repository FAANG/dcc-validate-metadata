package Bio::Metadata::Loader::XLSXLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use Spreadsheet::ParseExcel::Stream::XLSX;

requires 'process_sheet';

sub load {
	my ( $self, $file_path, $sheet_array) = @_;
	
	my %to_process = map { $_ => 1 } @$sheet_array;
	
	my @entities;
	
	my $xls = Spreadsheet::ParseExcel::Stream::XLSX->new($file_path);

	while ( my $sheet = $xls->sheet() ) {
		my $set;
		if (%to_process) {
			next unless exists($to_process{$sheet->name});
			$set=$self->process_sheet($sheet);
		} else {
	 		$set=$self->process_sheet($sheet);
		}
		if ($set!=0) {
			foreach my $e (@$set) {
				push @entities,$e
			}
		}
	}
	print "[WARNING] No entities retrieved from $file_path" if !@entities;
	return \@entities;
}

1;
