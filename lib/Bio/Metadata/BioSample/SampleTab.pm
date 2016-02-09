# Copyright 2015 European Molecular Biology Laboratory - European Bioinformatics Institute
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
package Bio::Metadata::BioSample::SampleTab;

use strict;
use warnings;
use Data::Dumper;

use Moose;
use namespace::autoclean;
use Bio::Metadata::Loader::XLSXBioSampleLoader;
use Moose::Util::TypeConstraints;

has 'scd'       => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'Bio::Metadata::EntityArrayRef',
    handles => {
        all_scd   => 'elements',
        add_scd    => 'push',
        count_scd => 'count',
        get_scd    => 'get',
    },
    default => sub { [] },
    coerce  => 1,
);

has 'msi'       => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'Bio::Metadata::EntityArrayRef',
    handles => {
        all_msi   => 'elements',
        add_msi    => 'push',
        count_msi => 'count',
        get_msi    => 'get',
    },
    default => sub { [] },
    coerce  => 1,
);

#define common FAANG attributes
my @COMMON= ("Sample Description","Material","Availability");
#different sheets in the Excel
my @SHEETS= ("organism", "tissue specimen", "cell specimen", "cell culture");
#accepeted Named Attributes. For definition see: https://www.ebi.ac.uk/biosamples/help/st_scd.html
my @NAMED= ("Organism", "Material", "Sex", "Sample Description");
#accepted Relationships. For definition see: https://www.ebi.ac.uk/biosamples/help/st_scd.html
my @RELATIONSHIPS= ("Same as","Derived from","Child of");

my %common=map {$_ => 1} @COMMON;
my %named=map {$_ => 1} @NAMED;
my %relationships=map {$_ => 1} @RELATIONSHIPS;


sub read {
	my ($self,$file_path)=@_;
	
	die("[ERROR] Please provide the path to a XLSX file") if !$file_path;
	
	my $loader = Bio::Metadata::Loader::XLSXBioSampleLoader->new();
	
	my $o=$loader->load($file_path);
	
	my @msi=grep{$_->entity_type eq 'msi'} @$o;
	my @scd=grep{$_->entity_type eq 'sample'} @$o;
	
	$self->msi(\@msi);
	$self->scd(\@scd);
}

sub print_msi {
	my ($self)=@_;
	
	print "[MSI]\n";
	my ($name,$uri,$version);
	foreach my $e (@{$self->msi}) {
		my $atts=$e->attributes;
		foreach my $a (@$atts) {
			next if !$a->value;
			if ($a->name=~/Term Source/) {
				$name.=$a->value."\t" if $a->name eq 'Term Source Name';
				$uri.=$a->value."\t" if $a->name eq 'Term Source URI';
				$version.=$a->value."\t" if $a->name eq 'Term Source Version';
			} else {
				print $a->name,"\t",$a->value,"\n";
			}
			
		}
	}
	print "Term Source Name\t$name\n" if defined $name;
	print "Term Source URI\t$uri\n" if defined $uri;
	print "Term Source Version\t$version\n" if defined $version;
	print "\n";
}

sub print_scd {
	my ($self)=@_;
	
#	my $fields=$self->parse_fields;
	
	my ($header,$str)=$self->generate_header;
	
	print "[SCD]\n";
	
	print "Sample Name","\t",$str,"\n";
	
	foreach my $e (@{$self->scd}) {
		print $e->id,"\t";
		my $atts=$e->organised_attr;
		foreach my $i (@$header) {
			my $a=$atts->{$i}->[0];
			if ($a) {
				print $a->value,"\t";
				if ($a->id) {
					my $ref=$1 if $a->id=~/(.+)_\d+/;
					$ref='NCBI Taxonomy' if $a->name eq 'Organism';
					die("[ERROR] I could not guess the Term Source REF from ",$a->id) if !$ref;
					print $ref,"\t",$a->id,"\t";
				}
				
			} else {
				print "\t\t";
			}
		}
		print "\n";
		
	}
	
	
}

sub generate_header {
	my ($self)=@_;
	
	my $mat_seen=0;
	my $common_seen=0;
	my @header;
	my $header_str;
	
	foreach my $e (@{$self->scd}) {
		my $atts=$e->organised_attr;
		if ($common_seen==0) {
			$common_seen=1;
			foreach my $c (@COMMON) {
				$header_str.=$c."\t";
				push @header, $atts->{$c}->[0]->name;
				$header_str.="Term Source REF\t" if $atts->{$c}->[0]->id;
				$header_str.="Term Source ID\t" if $atts->{$c}->[0]->id;			
			}
		}
		next if $mat_seen eq $atts->{'Material'}->[0]->value;
		$mat_seen=$atts->{'Material'}->[0]->value;
		foreach my $a (@{$e->attributes}) {
			next if exists($common{$a->name});
			push @header,$a->name;
			if (!exists($named{$a->name}) && !exists($relationships{$a->name})) {
				$header_str.="Characteristic[".$a->name."]\t";
			} else {
				$header_str.=$a->name."\t";
			}
			if ($a->id) {
				$header_str.="Term Source REF\t";
				$header_str.="Term Source ID\t";
			} elsif ($a->units) {
				$header_str.="Unit\t";
			}
		}
	}
	
	return (\@header,$header_str);
}

sub parse_fields {
	my ($self)=@_;
	
	my %fields;
	
	foreach my $e (@{$self->scd}) {
		my $atts=$e->organised_attr;
		my $mat=$atts->{'Material'}->[0]->value;
		if (!exists($fields{$mat})) {
			foreach my $a (@{$e->attributes}) {
				if (!exists($named{$a->name}) && !exists($relationships{$a->name})) {
					push @{$fields{$mat}},'Characteristic['.$a->name.']';
				} else {
					push @{$fields{$mat}},$a->name;
				}
				if ($a->id) {
					push @{$fields{$mat}}, 'Term Source REF';
					push @{$fields{$mat}}, 'Term Source ID';
				} elsif ($a->units) {
					push @{$fields{$mat}}, 'Unit';
				}
			}
		} 
	}
	return \%fields;
}

1;