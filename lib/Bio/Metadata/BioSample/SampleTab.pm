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
my @COMMON= ("Sample Name","Sample Description","Material","Availability");
	

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
	
	my %is_common = map {$_ => 1} @COMMON;
	my @fields=@COMMON;
	foreach my $e (@{$self->scd}) {
		foreach my $a (@{$e->attributes}) {
			next if exists($is_common{$a->name});
			push @fields,$a->name;
		}
	}
	print "h\n";
	
}

1;