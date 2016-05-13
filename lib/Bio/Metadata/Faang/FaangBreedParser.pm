
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

package Bio::Metadata::Faang::FaangBreedParser;

use Moose;
use namespace::autoclean;
use Carp;
use Data::Dumper;
use List::Util qw(any none);
use Bio::Metadata::Faang::FaangBreed;

my ( $sire, $dam ) = qw(sire dam);

=head1 parse
  $parser->parse($breed_text);

  interprets the breed text based on the FAANG breed spec and converts it to
  structured data

  returns a hash ref.

  Pure bred:
  'Breed A' returns {breeds => ['Breed A']}
  Mixed breed:
  'Breed A, Breed B' returns {breeds => ['Breed A', 'Breed B']}
  Crossbred:
  'Breed A sire x Breed B dam' returns {sire => 'Breed A',dam => 'Breed B'}
  Backcross etc.:
  'Breed A sire x (Breed B sire x Breed A dam) dam' returns
    {
      sire => 'Breed A',
      dam  => {
        sire => 'Breed B',
        dam => 'Breed A',
      }
    }
=cut

sub parse {
  my ( $self, $breed_text ) = @_;

  my @tokens = $self->_lexer($breed_text);
  my $b = $self->_parser(@tokens);
  return $b;
}

=head1 _parser
  $parser->_parser(@tokens);

  convert tokens to structured breed data, or an empty hash if it can't be
  understood
=cut

sub _parser {
  my ( $self, @tokens ) = @_;

  my $b;

  if ( any { $_ eq '(' } @tokens ) {
    $b = $self->_nested(@tokens);
  }
  elsif ( any { $_ eq 'x' } @tokens ) {
    $b = $self->_cross(@tokens);
  }
  elsif ( any { $_ eq ',' } @tokens ) {
    $b = $self->_mixed(@tokens);
  }
  else {
    $b = $self->_pure(@tokens);
  }

  return $b;
}

=head1 _nested
  $parser->_nested(@tokens);

  decode nested breed information.
=cut

sub _nested {
  my ( $self, @tokens ) = @_;

  my @opener;
  my @b;
  my @nested;
  
  for ( my $i = 0 ; $i < scalar(@tokens) ; $i++ ) {

    if ( $tokens[$i] eq '(' ) {
      push @nested, $tokens[$i] if @opener;
      push @opener, $i;
    }
    elsif ( $tokens[$i] eq ')' && @opener ) {
      pop @opener;
      if (@opener) {
        push @nested, $tokens[$i];
      }
      else {
        push @b, $self->_parser(@nested);
        @nested = ();
      }
    }
    elsif ( $tokens[$i] eq ')' && !@opener ) {
      return undef;    #unbalanced brackets
    }
    elsif (@opener) {
      push @nested, $tokens[$i];
    }
    else {
      push @b, $tokens[$i];
    }

  }

  if (@opener) {

    #unbalanced brackets, must be an error
    return undef;
  }

  return $self->_parser(@b);
}

sub _cross {
  my ( $self, @tokens ) = @_;

  my ($x_index) = grep $tokens[$_] eq 'x', 0 .. $#tokens;

  my @lhs = @tokens[ 0 .. ( $x_index - 1 ) ];
  my @rhs = @tokens[ ( $x_index + 1 ) .. $#tokens ];

  my %b;

  for my $a ( \@lhs, \@rhs ) {
    return {} if ( scalar( @$a < 2 ) );    #too few tokens to be valid

    my $k = pop @$a;                       # is this a sire or a dam?

    return undef if ( $k ne $sire && $k ne $dam );
    return undef if ( $b{$k} );            # too many parents of one sex given

    if ( ref $a->[0] ) {
      $b{$k} = $a->[0];
    }
    else {
      $b{$k} = join ' ', @$a;
    }
  }

  return Bio::Metadata::Faang::FaangBreed->new(%b);
}

sub _mixed {
  my ( $self, @tokens ) = @_;
  my @breeds;
  my @b;
  while ( my $t = shift @tokens ) {
    if ( $t eq ',' ) {
      push @breeds, join( ' ', @b ) if @b;
      @b = ();
    }
    else {
      push @b, $t;
    }
  }
  push @breeds, join( ' ', @b ) if @b;
  return Bio::Metadata::Faang::FaangBreed->new( breeds => \@breeds );
}

sub _pure {
  my ( $self, @tokens ) = @_;
  return Bio::Metadata::Faang::FaangBreed->new(
    breeds => [ join( ' ', @tokens ) ] );
}

=head1 parse
  $parser->_lexer($breed_text);

  tokenises the text, returning a list of words.
  each space delimted word is a token.
  Commas are treated as tokens.
  round brackets are treated as tokens, if they enclose signifcant delimiters
  from the spec i.e. '(',')', 'x' or ','. The aim is to allow for breed names
  that contain brackets.
=cut

sub _lexer {
  my ( $self, $text ) = @_;

  my @tokens;

  my $word_buffer = '';
  my $l           = length($text);

  for ( my $i = 0 ; $i < $l ; $i++ ) {
    my $c = substr( $text, $i, 1 );
    my $word_stop = 0;

    if ( $c eq '(' || $c eq ')' || $c eq ',' ) {
      push @tokens, $word_buffer if $word_buffer;
      push @tokens, $c;
      $word_buffer = '';
    }
    elsif ( $c =~ m/\s/ ) {
      push @tokens, $word_buffer if $word_buffer;
      $word_buffer = '';
    }
    else {
      $word_buffer .= $c;
    }
  }
  push @tokens, $word_buffer if $word_buffer;

  return $self->_lexer_cleanup(@tokens);
}

=head1 parse
  $parser->_lexer_cleanup(@tokens);

  cleanup the tokens, so that round brackets are only treated as tokens, if they
  enclose signifcant delimiters from the spec i.e. '(',')', 'x' or ','.
  The aim is to allow for breed names that contain brackets.
=cut

sub _lexer_cleanup {

  my ( $self, @tokens ) = @_;

  my @opener;
  my @b;
  my @nested;

  for ( my $i = 0 ; $i < scalar(@tokens) ; $i++ ) {

    if ( $tokens[$i] eq '(' ) {
      push @nested, $tokens[$i] if @opener;
      push @opener, $i;
    }
    elsif ( $tokens[$i] eq ')' && @opener ) {
      pop @opener;

      if ( !@opener ) {
        if ( any { $_ eq '(' || $_ eq ')' || $_ eq 'x' || $_ eq ',' } @nested )
        {
          push @b, '(', $self->_lexer_cleanup(@nested), ')';
        }
        elsif (@nested) {
          $nested[0]  = '(' . $nested[0];
          $nested[-1] = $nested[-1] . ')';
          push @b, @nested;
        }
        else {
          push @b, '(', ')';
        }

        @nested = ();
      }
      else {
        push @nested, $tokens[$i];
      }
    }
    elsif ( @opener && $i == scalar(@tokens) - 1 ) {    #last token
      push @b, '(', @nested, $tokens[$i];
    }
    elsif (@opener) {
      push @nested, $tokens[$i];
    }
    else {
      push @b, $tokens[$i];
    }

  }

  return @b;
}

__PACKAGE__->meta->make_immutable;
1;
