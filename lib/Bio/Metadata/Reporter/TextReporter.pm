
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

package Bio::Metadata::Reporter::TextReporter;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;
use Bio::Metadata::Reporter::AttributeColumn;
use Data::Dumper;

with "Bio::Metadata::Reporter::ReporterRole";

has 'file_path' => ( is => 'rw', isa => 'Str', required => 1 );
has 'max_size_msg' => (is => 'rw', isa => 'Int');


sub report {
    my ( $self, %params ) = @_;
    my $entities           = $params{entities};
    my $entity_status      = $params{entity_status};
    my $entity_outcomes    = $params{entity_outcomes};
    my $attribute_status   = $params{attribute_status};
    my $attribute_outcomes = $params{attribute_outcomes};


	$self->print($entity_outcomes);
}

sub print {
	my ($self,$entity_outcomes)=@_;

	open OUTFH,">",$self->file_path;
	print OUTFH "#id\tstatus\tmessage\tvalue\n";
	foreach my $e (keys %$entity_outcomes) {
		my @outcomes=@{$entity_outcomes->{$e}};
		foreach my $o (@outcomes) {
      my $msg = $o->message;
      if ($o->message && $self->max_size_msg && length($msg) > $self->max_size_msg){
        $msg =substr($o->message,0,$self->max_size_msg)
      }

			if ($o->outcome eq 'error') {
				print OUTFH $o->entity->id,"\t",$o->outcome,"\t'",$msg,"'\tNA\n";
			} elsif ($o->outcome eq 'warning') {
				print OUTFH $o->entity->id,"\t",$o->outcome,"\t'",$msg,"'\t",$o->attributes->[0]->value,"\n";
			}
		}
	}

	close OUTFH;
}


__PACKAGE__->meta->make_immutable;

1;
