
=head1 LICENSE
   Copyright 2016 EMBL - European Bioinformatics Institute
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

package Bio::Metadata::Validate::UriValueAttributeValidator;

use strict;
use warnings;

use Moose;
use Try::Tiny;
use URI;
use namespace::autoclean;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'supported_schema' => (
    traits  => ['Array'],
    is      => 'rw',
    isa     => 'ArrayRef[Str]',
    default => sub { return [qw(http https ftp mailto)] },
    handles => {
        find_supported_schema => 'first',
        join_supported_schema => 'join',
    },
);

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    if ( !defined $attribute->value ) {
        $o->outcome('error');
        $o->message('no value provided');
        return $o;
    }

    my $uri;
    try {
        $uri = URI->new( $attribute->value );
    }
    catch {
        $o->outcome('error');
        $o->message('value is not a URI');
        return $o;
    };

    if ( !$uri->has_recognized_scheme ) {
        $o->outcome('error');
        $o->message('value is not a URI');
        return $o;
    }

    if ( !$self->find_supported_schema( sub { $uri->scheme eq $_ } ) ) {
        $o->outcome('error');
        $o->message( 'uri scheme is not supported. It is '
              . $uri->scheme
              . ' but only '
              . $self->join_supported_schema(', ')
              . ' are accepted' );
        return $o;
    }

    if ($uri->scheme ne "mailto"){
        unless ($attribute->value =~ /^((http|ftp)s?:\/\/)?(www\.)?[-a-zA-Z0-9\@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9\@:%_\+.~#?&\/=]*)$/) {
            $o->outcome('error');
            $o->message('Invalid URL');
            return $o;
        }
    }

    $o->outcome('pass');
    return $o;
}

__PACKAGE__->meta->make_immutable;
1;
