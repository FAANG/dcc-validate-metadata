use XML::Simple;
$file = XMLin('/Users/ernesto/scripts/validate/t/data/sample_set.xml',KeepRoot=> 1);

foreach $sample (@{$file->{SAMPLE_SET}->{SAMPLE}})    {
    print "TITLE: " . $sample->{TITLE} ." \n";

}
