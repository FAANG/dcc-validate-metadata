use Point;
use strict;
use warnings;

my $p = Point->new(x => 10, y => 10);

my $pack=$p->pack();

my $A=$p->freeze();

print "h\n";
