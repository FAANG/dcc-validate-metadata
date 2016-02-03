package Bio::Metadata::Loader::XLSXLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;
use Spreadsheet::Read;


sub load {
	my ( $self, $file_path ) = @_;
	
	my $workbook = ReadData($file_path);
	
	die("[ERROR] parsing $file_path. Please check the file") if ( !defined $workbook );
	
	my @rows = Spreadsheet::Read::rows($workbook->[2]);
	
	my $header=$rows[0];
	shift @rows;
	my %fields= map { $_ => 1 } split/\t/,$header;
	
	
	foreach my $i (1 .. scalar @rows) {
	    foreach my $j (1 .. scalar @{$rows[$i-1]}) {
	        print "start:",$rows[$i-1][$j-1],":end\t";
	    }
	}
	
}

1;