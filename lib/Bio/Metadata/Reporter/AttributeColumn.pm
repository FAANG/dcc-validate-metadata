
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

package Bio::Metadata::Reporter::AttributeColumn;

use strict;
use warnings;

use Carp;
use Moose;
use autodie;
use namespace::autoclean;

has 'name' => ( is => 'rw', isa => 'Str', required => 1 );
has [ 'use_units', 'use_uri', 'use_ref_id' ] =>
  ( is => 'rw', isa => 'Bool', required => 1, default => '' );
has 'max_count' => (
    is       => 'rw',
    isa      => 'Int',
    required => 1,
    default  => 0,
);

has 'term_count' => (
    traits   => ['Hash'],
    is       => 'rw',
    isa      => 'HashRef[HashRef[Int]]',
    default  => sub { { value => {}, uri => {}, units => {}, ref_id => {} } },
    required => 1,
    handles => { categories => 'keys' }
);

has 'probable_duplicates' => (
    traits => ['Hash'],
    is     => 'rw',
    isa    => 'HashRef[HashRef[Str]]',
    default => sub { { value => {}, uri => {}, units => {}, ref_id => {} } },
);

sub consume_attrs {
    my ( $self, $attrs ) = @_;

    if ( scalar(@$attrs) > $self->max_count ) {
        $self->max_count( scalar(@$attrs) );
    }

    for my $a (@$attrs) {
        $self->use_units(1) if ( $a->units );
        $self->use_uri(1)   if ( $a->uri );

        if ( defined $a->value ) {
            $self->term_count()->{value}{ $a->value }++;
        }
        if ( $a->uri ) {
            $self->term_count()->{uri}{ $a->uri }++;
        }
        if ( $a->units ) {
            $self->term_count()->{units}{ $a->units }++;
        }
    }

    for my $c ( $self->categories ) {
        my %term_count = %{$self->term_count()->{$c}};
        my %term_mash;

        for my $k ( keys %term_count ) {
            my $mashed_term = _mash_term($k);
            $term_mash{$mashed_term}++;

            if ( $term_mash{$mashed_term} == 2 ) {
                $self->probable_duplicates()->{$c}{$k} = $k;
            }
        }

    }
}

sub _mash_term {
    my ($term) = @_;
    my $mashed = lc($term);
    $mashed =~ s/\W//g;    # remove anything that isn't a-z,1-0,_
    return $mashed;
}

__PACKAGE__->meta->make_immutable;

1;
