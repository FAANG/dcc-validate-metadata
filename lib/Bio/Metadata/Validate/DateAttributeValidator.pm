
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

package Bio::Metadata::Validate::DateAttributeValidator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;
use Carp;

use DateTime::Format::ISO8601;
use Try::Tiny;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'valid_formats' => (
    traits  => ['Hash'],
    is      => 'rw',
    isa     => 'HashRef[RegexpRef]',
    default => sub {
        return {
            'YYYY-MM-DD' => qr/\d{4}-\d{2}-\d{2}/,
            'YYYY-MM'    => qr/\d{4}-\d{2}/,
            'YYYY'       => qr/\d{4}/,
        };
    },
    handles => { get_valid_format => 'get', all_valid_formats => 'keys' },
);

sub join_valid_formats {
    my ( $self, $delimiter ) = @_;
    return join( $delimiter, $self->all_valid_formats );

}

sub validate_date {
    my ( $self, $value, $date_format ) = @_;

    if ( !$self->get_valid_format($date_format) ) {
        return ( undef,
"Date format in units is not understood by the validator. Got $date_format, can accept "
              . $self->join_valid_formats(', ') );
    }

    if ( $value !~ $self->get_valid_format($date_format) ) {
        return ( undef,
            "Date $value does not match the expected format $date_format" );
    }

    my $dt;
    try {
        $dt = DateTime::Format::ISO8601->parse_datetime($value);
    }
    catch {
#DateTime will die for extremely invalid dates (e.g. doesn't match format)
#DateTime will return undef for things that match format, but aren't real dates, e.g. 32nd day of January
        $dt = undef;
    };

    if ( !$dt ) {
        return ( undef, "Date $value is not a valid date" );
    }

    return ( $dt, undef );
}

sub check_rule_units {
    my ( $self, $rule ) = @_;

    for my $rule_unit ( @{ $rule->valid_units } ) {
        my $match = $self->get_valid_format($rule_unit);
        if ( !$match ) {
            croak(
"Rule has units that aren't a supported date format. Received $rule_unit, but accepts "
                  . $self->join_valid_formats(', ') );
        }
    }
}

sub validate_attribute {
    my ( $self, $rule, $attribute, $o ) = @_;

    $self->check_rule_units($rule);

    if ( !defined $attribute->value ) {
        $o->outcome('error');
        $o->message('no value provided');
        return $o;
    }
    if ( !defined $attribute->units ) {
        $o->outcome('error');
        $o->message('no units provided');
        return $o;
    }

    my $date_string = $attribute->value;
    my $date_format = $attribute->units;
    my ( $date, $error_msg ) =
      $self->validate_date( $date_string, $date_format );

    if ($error_msg) {
        $o->outcome('error');
        $o->message($error_msg);
    }
    else {
        $o->outcome('pass');
    }

    return $o;
}
__PACKAGE__->meta->make_immutable;
1;
