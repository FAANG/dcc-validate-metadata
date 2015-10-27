package main;
use JSON;
use Emp;

my $JSON = JSON->new->utf8;
$JSON->convert_blessed(1);

$e = new Emp( "sachin", "sports", "8/5/1974 12:20:03 pm");
$json = $JSON->pretty->encode($e);
print "$json\n";
