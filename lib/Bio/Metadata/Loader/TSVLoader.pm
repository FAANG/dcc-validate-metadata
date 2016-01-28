
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

package Bio::Metadata::Loader::TSVLoader;

use strict;
use warnings;

use Carp;
use Moose;
use Data::Dumper;
use namespace::autoclean;
use Bio::Metadata::Entity;

sub load {
  	my ( $self, $file_path )  = @_;
  
  	my (@lines,$o);
  
  	open my $handle, '<', $file_path or die("Cant open $file_path:$!\n");
  	@lines = <$handle>;
  	close $handle;
	
  	if (scalar(@lines)==0) {
		croak "[ERROR] No records in $file_path";
	} elsif($lines[0]!~/^TYPE\t/) {
		croak "[ERROR] $file_path needs to start with a header row";
	}
	
	my $header=$lines[0];
	shift @lines;
	
	my %fields= map { $_ => 1 } split/\t/,$header;	
	
	&validate_header(\%fields);
	
	if (scalar(@lines)==1) {
		$o = $self->line_to_object($lines[0],$header);
	} else {
		$o = [ map { $self->line_to_object($_,$header) } @lines ];
	}
	
	return $o;
}

sub validate_header {
	my $fields=shift;
	
	croak("[ERROR]. I need a 'TYPE' field in the tsv file") if !exists($fields->{'TYPE'});
	croak("[ERROR]. I need a 'TITLE' field in the tsv file") if !exists($fields->{'TITLE'});
	
}

sub line_to_object {
	my ($self,$line,$header)=@_;
	
	my @fields=split/\t/,$header;
	my @elems=split/\t/,$line;
  
  	croak("[ERROR] Number of fields in the header/rows does not match") if scalar(@fields)!=scalar(@elems);
	
	my %hash;
	for (my $i=0; $i<scalar(@fields); $i++) {
		$fields[$i]=~s/^\s|\s$//g;
		$elems[$i]=~s/^\s|\s$//g;
		$hash{$fields[$i]}=$elems[$i];
	}
  	
	my $o = Bio::Metadata::Entity->new();
	$o->id($hash{'TITLE'});
	$o->entity_type($hash{'TYPE'});
	
	delete $hash{'TITLE'};
	delete $hash{'TYPE'};
	
    #set 'attributes' in Entity.pm
    #arrayref of hashes
    foreach my $key (keys %hash) {
		my $o_attrb= Bio::Metadata::Attribute->new(
				name => $key,
  				value => $hash{$key}
  				);
		$o->add_attribute($o_attrb);
    }
	
	return $o;
}

__PACKAGE__->meta->make_immutable;
1;
