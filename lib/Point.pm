package Point;
use Moose;
use MooseX::Storage;

with Storage('format' => 'JSON');

has 'x' => (is => 'rw', isa => 'Int');
has 'y' => (is => 'rw', isa => 'Int');

1;
