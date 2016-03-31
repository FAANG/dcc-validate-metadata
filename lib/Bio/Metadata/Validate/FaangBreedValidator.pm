
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

package Bio::Metadata::Validate::FaangBreedValidator;

use strict;
use warnings;

use Moose;
use namespace::autoclean;

use Bio::Metadata::Validate::Support::FaangBreedParser;
use Bio::Metadata::Validate::Support::OlsLookup;
use Bio::Metadata::Validate::OntologyTextAttributeValidator;
use Bio::Metadata::Rules::PermittedTerm;

with 'Bio::Metadata::Validate::AttributeValidatorRole';

has 'breed_parser' => (
  is  => 'ro',
  isa => 'Bio::Metadata::Validate::Support::FaangBreedParser',
  default =>
    sub { return Bio::Metadata::Validate::Support::FaangBreedParser->new() }
);

has 'ols_lookup' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Validate::Support::OlsLookup',
  default => sub { return Bio::Metadata::Validate::Support::OlsLookup->new() }
);

has 'valid_term' => (
  is      => 'rw',
  isa     => 'Bio::Metadata::Rules::PermittedTerm',
  default => sub {
    Bio::Metadata::Rules::PermittedTerm->new(
      ontology_name     => 'LBO',
      allow_descendants => 1,
      leaf_only         => 1,
      include_root      => 0,
      term_iri          => 'http://purl.obolibrary.org/obo/LBO_0000000',
    );
  }
);

sub validate_attribute {
  my ( $self, $rule, $attribute, $o ) = @_;

  if ( !defined $attribute->value ) {
    $o->outcome('error');
    $o->message('no value provided');
    return $o;
  }

  my $animal_breeds = $self->breed_parser()->parse( $attribute->value );

  if ( !$animal_breeds ) {
    return $self->_parse_error($o);
  }

  if ( $animal_breeds->{breeds} ) {
    #mixed or pure
    return $self->validate_pure_or_mixed( $rule, $animal_breeds, $attribute,
      $o );
  }

  return $self->validate_cross($rule, $animal_breeds, $attribute,
    $o );
  }

sub validate_cross {
  my ( $self, $rule, $animal_breeds, $attribute, $o ) = @_;


  my ($breeds,$max_depth) = $self->_check_sire_and_dam($animal_breeds,0,$o);

  if ($o->outcome && $o->outcome ne 'pass'){
    return $o;
  }

  if ($max_depth > 2){
    return $self->_parse_error($o);
  }

  my %u_breeds = map {$_ => 1} @$breeds;
  @$breeds = sort keys %u_breeds;

  for my $b (@$breeds){
    my $match = $self->lookup_breed($b);
    if (!$match){
      return $self->_breed_match_error($o,$b);
    }
  }

  if (scalar(@$breeds) < 2){
    return $self->_parse_error($o);
  }

  $o->outcome('pass');

  return $o;
}

sub _check_sire_and_dam {
  my ($self,$animal_breeds,$callers_depth, $o) = @_;

  my $curr_depth = $callers_depth+1;
  my $max_depth = $curr_depth;
  my @breeds;

  for my $k (qw(sire dam)) {
    my $v = $animal_breeds->{$k};

    if (!defined $v){
      $self->_parse_error($o);
    }
    elsif (ref $v){
        my ($b,$d) = $self->_check_sire_and_dam($v,$curr_depth,$o);
        $max_depth = $d if ($d>$max_depth);
        push @breeds, @$b;
    }
    else {
      push @breeds, $v;
    }

    if ($o->outcome && $o->outcome ne 'pass'){
      return (\@breeds,$max_depth);
    }
  }

  return (\@breeds,$max_depth);
}

sub validate_pure_or_mixed {
  my ( $self, $rule, $animal_breeds, $attribute, $o ) = @_;

  my @breeds = @{ $animal_breeds->{breeds} };

  for my $b (@breeds) {
    my $match = $self->lookup_breed($b);

    if ( !$match ) {
      return $self->_breed_match_error($o,$b);
    }

    if ( scalar(@breeds) == 1 ) {
      my $id = $attribute->id;
      if ( defined $id
        && $id ne $match->obo_id
        && $id ne $match->short_form )
      {
        $o->outcome('warning');
        $o->message("breed name '$b' does not seem consistent with ID '$id'");
        return $o;
      }
    }
  }

  $o->outcome('pass');
  return $o;
}

sub lookup_breed {
  my ($self,$breed) = @_;
  return $self->ols_lookup->find_match( $breed, $self->valid_term, 1 );
}

sub _parse_error {
  my ($self,$o) = @_;
  $o->outcome('error');
  $o->message('could not parse breed');
  return $o;
}

sub _breed_match_error {
  my ($self,$o,$b) = @_;
  $o->outcome('error');
  $o->message("cannot find breed '$b' in ontology");
  return $o;
}

__PACKAGE__->meta->make_immutable;
1;
