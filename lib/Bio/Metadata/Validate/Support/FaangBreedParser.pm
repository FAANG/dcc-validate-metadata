
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

package Bio::Metadata::Validate::Support::FaangBreedParser;

use Moose;
use namespace::autoclean;
use Carp;
use Data::Dumper;
use List::Util qw(any none);

my ( $sire, $dam ) = qw(sire dam);

sub parse {
  my ( $self, $breed_text ) = @_;

  my @tokens = $self->_lexer($breed_text);

  return $self->_parser(@tokens);
}

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

sub _nested {
  my ( $self, @tokens ) = @_;

  my @opener;
  my @b;
  my @nested;

  for ( my $i = 0 ; $i < scalar(@tokens) ; $i++ ) {

    if ( $tokens[$i] eq '(' ) {
      push @opener, $i;
    }
    elsif ( $tokens[$i] eq ')' && @opener ) {
      pop @opener;
      if ( !@opener ) {
        push @b, $self->_parser(@nested);
        @nested = ();
      }
    }
    elsif ( $tokens[$i] eq ')' && !@opener ) {
      return {};    #unbalanced brackets
    }
    elsif (@opener) {
      push @nested, $tokens[$i];
    }
    else {
      push @b, $tokens[$i];
    }

  }
  print Dumper( \@b, \@opener );

  if (@opener) {

    #unbalanced brackets, must be an error
    return {};
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

    return {} if ( $k ne $sire && $k ne $dam );
    return {} if ( $b{$k} );               # too many parents of one sex given

    if ( ref $a->[0] ) {
      $b{$k} = $a->[0];
    }
    else {
      $b{$k} = join ' ', @$a;
    }
  }

  return \%b;
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
  return { breeds => \@breeds };
}

sub _pure {
  my ( $self, @tokens ) = @_;
  return { breeds => [ join( ' ', @tokens ) ] };
}

#tokenise the text
# These chars are significant: ()x,
# Spaces are delimiters, but aren't significant otherwise
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

  my @checked_tokens;
  #some breeds have brackets in their names.
  while (@tokens) {
    my $t = pop @tokens;    #start at the end

    if (
      $t eq ')'
      && ( !@checked_tokens
        || none { $checked_tokens[0] eq $_ } ( $sire, $dam ) )
      && @tokens
      )
    {
        unshift @checked_tokens, (pop @tokens).$t;

        while (@tokens){
          my $s = pop @tokens;
          if ($s eq '(') {
            $checked_tokens[0] = $s.$checked_tokens[0];
            last;
          }
          else{
            unshift @checked_tokens, $s;
          }
        }
    }
    else {
      unshift @checked_tokens, $t;
    }

    print STDERR Dumper($t,@tokens,@checked_tokens);

  }

  return @checked_tokens;

}

__PACKAGE__->meta->make_immutable;
1;
