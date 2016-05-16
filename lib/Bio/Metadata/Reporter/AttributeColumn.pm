
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
has [ 'use_units', 'use_uri', 'use_ref_id', 'use_source_ref', 'use_id' ] =>
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
  traits  => ['Hash'],
  is      => 'rw',
  isa     => 'HashRef[HashRef[Str]]',
  default => sub { { value => {}, uri => {}, units => {}, ref_id => {} } },
);

sub to_hash {
  my ($self) = @_;

  return {
    name                => $self->name,
    term_count          => $self->term_count,
    max_count           => $self->max_count,
    probable_duplicates => $self->probable_duplicates,
  };
}

sub consume_attrs {
  my ( $self, $attrs ) = @_;

  if ( scalar(@$attrs) > $self->max_count ) {
    $self->max_count( scalar(@$attrs) );
  }

  my $use_units      = $self->use_units;
  my $use_uri        = $self->use_uri;
  my $use_ref_id     = $self->use_ref_id;
  my $use_source_ref = $self->use_source_ref;
  my $use_id         = $self->use_id;

  for my $a (@$attrs) {
    if ( defined $a->value ) {
      $self->term_count()->{value}{ $a->value }++;
    }
    if ( defined $a->uri ) {
      $self->term_count()->{uri}{ $a->uri }++;
      $use_uri = 1;
    }
    if ( defined $a->units ) {
      $self->term_count()->{units}{ $a->units }++;
      $use_units = 1;
    }
    if ( defined $a->id || defined $a->source_ref ) {
      $self->term_count()->{ref_id}{ $a->source_ref_id }++;
      $use_ref_id = 1;
    }
    $use_id         = 1 if ( defined $a->id );
    $use_source_ref = 1 if ( defined $a->source_ref );
  }
  $self->use_units($use_units);
  $self->use_uri($use_uri);
  $self->use_ref_id($use_ref_id);
  $self->use_source_ref($use_source_ref);
  $self->use_id($use_id);

  my %mashed_terms;

  for my $c ( $self->categories ) {
    my %term_count = %{ $self->term_count()->{$c} };
    my %term_mash;

    for my $k ( keys %term_count ) {
      if ( !exists $mashed_terms{$k} ) {

        #mash term
        $mashed_terms{$k} = lc($k);
        $mashed_terms{$k} =~ s/\W//g;    # remove anything that isn't a-z,1-0,_
      }
      $term_mash{ $mashed_terms{$k} }++;
    }

    for my $k ( keys %term_count ) {
      if ( $term_mash{ $mashed_terms{$k} } > 1 ) {
        $self->probable_duplicates()->{$c}{$k} = $k;
      }
    }

  }
}

__PACKAGE__->meta->make_immutable;

1;
