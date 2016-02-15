=head1 LICENSE
   Copyright 2015 EMBL - European Bioinformatics Institute
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
=cut

package Bio::Metadata::Loader::XLSXBioSampleLoader;

use strict;
use warnings;

use FindBin qw/$Bin/;
use lib "$Bin/../lib";

use Encode::Guess;
use Encode qw(encode decode);
use Moose;
use Carp;
use Data::Dumper;
use namespace::autoclean;
use Bio::Metadata::Entity;

with "Bio::Metadata::Loader::XLSXLoaderRole";


sub process_sheet {
	my ( $self, $sheet) = @_;
	
	return 0 unless $sheet->name eq 'animal' || $sheet->name eq 'specimen' || $sheet->name eq 'purified cells' || $sheet->name eq 'cell culture'
	|| $sheet->name eq 'submission' || $sheet->name eq 'person' || $sheet->name eq 'organization' || $sheet->name eq 'publication' || $sheet->name eq 'database' || $sheet->name eq 'term source';
	
	my $fields= $sheet->row;	
	
	my @entities;
    while ( my $row = $sheet->row ) {
		my $e=$self->row_to_object($row,$fields,$sheet->name);
		if ($e!=0) {
			push @entities,$e;
		}
    }
	return \@entities;
}

sub row_to_object {
	my ($self, $row,$fields,$sheet_name) = @_;
	
	return 0 unless grep {defined($_)} @$row;
	
  	croak("[ERROR] Number of fields in the header/rows does not match") if scalar(@$fields)!=scalar(@$row);

	my $o = Bio::Metadata::Entity->new();	
	
	my $index=0;
	if ($sheet_name eq 'animal' || $sheet_name eq 'specimen' || $sheet_name eq 'purified cells' || $sheet_name eq 'cell culture') {
		$o->id($row->[0]);
		$o->entity_type('sample');
		$index=1;
	} elsif ($sheet_name eq 'submission' || $sheet_name eq 'person' || $sheet_name eq 'organization' || $sheet_name eq 'publication' || 
		$sheet_name eq 'database' || $sheet_name eq 'term source') {
		$o->id($sheet_name);
		$o->entity_type('msi');	
	}

	my $pr_att;
    for (my $i=$index;$i<scalar(@$row);$i++) {
		my $name=$fields->[$i];
		if ($name=~/([^[:ascii:]])/) {
			warn("[INFO] Non-ascii characters in '",$name,"'. These will be deleted\n");
			$name=~s/[^[:ascii:]]/ /g;
			$name=~s/\s{2}/ /;
			$name=~s/^\s|\s$//g;
		} elsif($row->[$i]=~/([^[:ascii:]])/) {
			warn("[INFO] Non-ascii characters in '",$row->[$i],"'. These will be deleted\n");
			$row->[$i]=~s/[^[:ascii:]]/ /g;
			$row->[$i]=~s/\s{2}/ /;
			$row->[$i]=~s/^\s|\s$//g;
		}
		next if $name eq 'Term Source REF';
		if ($name eq 'Term Source ID') {
			my $org_atts=$o->organised_attr;
			my $attr=$org_atts->{$pr_att}->[0];
			$attr->id($row->[$i]);
		} elsif ($name eq 'Unit') {
			my $org_atts=$o->organised_attr;
			my $attr=$org_atts->{$pr_att}->[0];
			$attr->units($row->[$i]);
		} else {
		
			my $o_attrb= Bio::Metadata::Attribute->new(
					name => $name,
  					value => $row->[$i]
 					);
			$o->add_attribute($o_attrb);
		}
    	$pr_att=$name;
    }	
	return $o;
}


__PACKAGE__->meta->make_immutable;
1;