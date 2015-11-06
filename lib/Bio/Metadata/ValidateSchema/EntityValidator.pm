
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

package Bio::Metadata::ValidateSchema::EntityValidator;

use strict;
use warnings;

use Carp;
use Moose;
use namespace::autoclean;
use JSON;
use JSON::Validator;

use Data::Dumper;
use Bio::Metadata::Entity;
use MooseX::Params::Validate;

has 'schema' => (
		 is => 'rw',
		 isa => 'Str',
		 required => 1
		);
has 'entity' => (
		 is => 'rw',
		 isa => 'Bio::Metadata::Entity',
		 required => 1
		);

sub validate {
  my ($self)=@_;

  my $hash=$self->entity->to_hash();

  #prepare attributes for validation
  my @attrbs=@{$hash->{'attributes'}};
  for (my $i=0;$i<scalar(@attrbs);$i++) {
    my $oldhash=$attrbs[$i];
    my %newhash=(
		 $oldhash->{'name'} => $oldhash->{'value'}
		);
    $attrbs[$i]=\%newhash;
		 
  }

  $hash->{'attributes'}=\@attrbs;
  print Dumper($hash),"\n";
  
  my $validator = JSON::Validator->new;
  $validator->schema($self->schema());

  my @errors = $validator->validate($hash);

  if (@errors) {
    foreach my $e (@errors) {
      
      #my $number=$1 if $e->path=~/\/attributes\/(\d+):/;
      print ref($e->path),"adios\n";
#      my $attr=$attrbs[$number-1];
      print "hello\n"
    }
  }

  print "hello\n";
}


1;
