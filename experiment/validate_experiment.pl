use strict;
use warnings;
use JSON::Validator;
use XML::Simple;
use JSON;
binmode STDOUT, ":utf8";
use utf8;

my $xml_file='experiment.stripped.xml';
my $schema_file='/Users/ernesto/scripts/metadata_work/experiments/experiment.schema.json';

my $xml = new XML::Simple;
my $data = $xml->XMLin($xml_file);

#read-in JSON schema
my $validator = JSON::Validator->new;
$validator->schema($schema_file);

my @errors = $validator->validate($data);

die "@errors" if @errors;

