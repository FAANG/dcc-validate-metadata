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
use utf8;
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
	
	my ($header_hash,$str,$sheets,$offsets)=$self->generate_header;
	
	print "[SCD]\n";
	
	print "Sample Name","\t",$str,"\n";
	
	foreach my $e (@{$self->scd}) {
		my $row=$e->id."\t";
		my $atts=$e->organised_attr;
		my $mat=$atts->{'Material'}->[0]->value;
		my $ix=0;
		foreach my $c (@COMMON) {
			my $a=$atts->{$c}->[0];
			$row=$self->_add_attribute($a,$row);
		}
		foreach my $s (@$sheets) {
			if ($s ne $mat) {
				my $a=$sheets->[$ix+1];
				my $b=$sheets->[$ix];
				my $offset;
				if (!defined($a)) {
					$offset=$offsets->{'total'}-$offsets->{$b};
				} else {
					$offset=$offsets->{$a}-$offsets->{$b};
				}
				$row.="\t"x$offset;
			} else {
				foreach my $i (@{$header_hash->{$mat}}) {
					my $a=$atts->{$i}->[0];
					$row=$self->_add_attribute($a,$row);
				}
			}
			$ix++;
		}
		
		print $row,"\n";
	}
	
	
}

sub _add_attribute {
	my ($self,$a,$row)=@_;
	if (defined($a->value)) {
		$row.=$a->value."\t";
		if (defined($a->id)) {
			my $ref="";
			$ref=$1 if $a->id=~/(.+)_\d+/;
			$ref='NCBI Taxonomy' if $a->name eq 'Organism';
			$row.=$ref."\t".$a->id."\t";
		}
		if (defined($a->units)) {
			my $unit=$a->units;
			$row.= $a->units."\t";
		}			
	}
	return $row;
}

sub generate_header {
	my ($self)=@_;
	
	my $mat_seen=0;
	my $common_seen=0;
	my %header_hash;
	my $header_str;
	my @sheets;
	my %offsets;
	my $counter=0;
	
	foreach my $e (@{$self->scd}) {
		my $atts=$e->organised_attr;
		my $mat=$atts->{'Material'}->[0]->value;
		if ($common_seen==0) {
			$common_seen=1;
			foreach my $c (@COMMON) {
				$header_str.=$c."\t";
				$header_str.="Term Source REF\t" if $atts->{$c}->[0]->id;
				$header_str.="Term Source ID\t" if $atts->{$c}->[0]->id;			
			}
		}
		
		next if $mat_seen eq $mat;
		push @sheets,$mat;
		$offsets{$mat}=$counter;
		$mat_seen=$atts->{'Material'}->[0]->value;
		foreach my $a (@{$e->attributes}) {
			next if exists($common{$a->name});
			push @{$header_hash{$mat}},$a->name;
			$counter++;
			if (!exists($named{$a->name}) && !exists($relationships{$a->name})) {
				$header_str.="Characteristic[".$a->name."]\t";
			} else {
				$header_str.=$a->name."\t";
			}
			if (defined($a->id)) {
				$counter++;
				$header_str.="Term Source REF\t";
				$counter++;
				$header_str.="Term Source ID\t";
			} elsif (defined($a->units)) {
				$counter++;
				$header_str.="Unit\t";
			}
		}
	}
	$offsets{'total'}=$counter;
	
	return (\%header_hash,$header_str,\@sheets,\%offsets);
}

1;