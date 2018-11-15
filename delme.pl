use DateTime;

my $str = "2018-11-01";
my $dt = &convertToDateTime($str);
my $type = ref($dt);
if ($type eq "DateTime"){
	print "predicted\n";
}else{
	print "wrong date value\n";
}
print "$dt\n";

sub convertToDateTime(){
	my $isoStr = $_[0];
	unless ($isoStr =~/^\d.+\d$/){
		return "Error: wrong date value $isoStr";
	}
	print "$isoStr\n";
	my @elem = split ("-",$isoStr);
	$"=">,<";
	print "@elem\n";
	my $len = scalar @elem;
	my $year;
	return "Input date not in the YYYY-MM-DD or YYYY-MM or YYYY format" if ($len > 3);
	unless ($elem[0]=~/^\d{4,4}$/){
		return "Error: unrecognized year value $elem[0]";
	}
	if ($len > 1){
		unless ($elem[1]=~/^\d{2,2}$/){
			return "Error: unrecognized month value $elem[1]";
		}
	}
	if ($len == 3){
		unless ($elem[2]=~/^\d{2,2}$/){
			return "Error: unrecognized day value $elem[2]";
		}
	}
	return DateTime->new(year => $elem[0]) if ($len == 1);
	return DateTime->new(year => $elem[0], month => $elem[1]) if ($len == 2);
	return DateTime->new(year => $elem[0], month => $elem[1], day => $elem[2]) if ($len == 3);
}
