#!/usr/bin/env perl
use strict;

use Bio::Metadata::Loader::JSONRuleSetLoader;
use Getopt::Long;
use Data::Dumper;
use Try::Tiny;
use Carp;

my $rule_file = undef;
my $verbose = undef;

#quick script to test rule sets load
GetOptions( "rules=s" => \$rule_file, "verbose" => \$verbose );

croak "-rules <file> is required" unless $rule_file;
croak "-rules <file> must exist and be readable" unless -r $rule_file;

my $loader = Bio::Metadata::Loader::JSONRuleSetLoader->new();
print "Attempting to load $rule_file$/" if $verbose;

try {
my $rules = $loader->load($rule_file);

if ($verbose){
  print Dumper($rules);
}
else {
  print 'Rule set: '.$rules->name.$/;
  print 'Description: '.($rules->description//'').$/.'Groups:'.$/;
  for my $rg ( $rules->all_rule_groups ) {
    print
      join( ' ', "\t".$rg->name, 'with', $rg->count_rules, 'rules'.$/ );
  }
}
exit 0;
} catch {
  print "Could not load rule set in $rule_file. Error:$/$_";
  exit 1;
}
