
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

package Bio::Metadata::Loader::XMLLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;

use XML::Simple;
use Try::Tiny;
use autodie;
use Data::Dumper;
use MooseX::Params::Validate;
use Bio::Metadata::Types;

requires 'hash_to_object';

sub load {
    my ( $self, $file_path ) = @_;

    my ( $xml_data, $o );
    
    try {
      my $xml = new XML::Simple;
      $xml_data = $xml->XMLin($file_path,KeepRoot => 1);
    }
    catch {
        croak "Failed to read from $file_path: $_";
    };

   try {
        if ( ref $xml_data eq 'HASH' ) {
            $o = $self->hash_to_object($xml_data);
        }
        elsif ( ref $xml_data eq 'ARRAY' ) {
            $o = [ map { $self->hash_to_object($_) } @$xml_data ];
        }
    }
    catch {
        croak "Could not convert data structure to object: $_";
    };
    return $o;
}

1;
