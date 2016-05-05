
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

package Bio::Metadata::Loader::JSONLoaderRole;

use strict;
use warnings;

use Carp;
use Moose::Role;

use JSON::MaybeXS qw(decode_json);
use Try::Tiny;
use autodie;
use Data::Dumper;
use MooseX::Params::Validate;
use Bio::Metadata::Types;

requires 'hash_to_object';

sub _load_blob {
    my ( $self, $blob, $src_name ) = @_;

    my ( $json_data, $o );
    try {
        $json_data = decode_json($blob);
    }
    catch {
        croak "Could not convert contents of $src_name to JSON: $_";
    };

    try {
        if ( ref $json_data eq 'HASH' ) {
            $o = $self->hash_to_object($json_data);
        }
        elsif ( ref $json_data eq 'ARRAY' ) {
            $o = [ map { $self->hash_to_object($_) } @$json_data ];
        }

    }
    catch {
        croak "Could not convert data structure to object: $_";
    };

    return $o;
}

sub load {
    my ( $self, $location ) = @_;

    my $json_text;
    try {
        open( my $fh, '<', $location );
        local $/ = undef;
        $json_text = <$fh>;
        close($fh);
    }
    catch {
        croak "Failed to read from $location: $_";
    };

    return $self->_load_blob($json_text, $location);
}

1;
