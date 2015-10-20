requires 'Moose';
requires 'JSON';
requires 'JSON::XS';
requires 'JSON::Validator';

on 'build' => sub {
  requires 'Module::Build::Pluggable';
  requires 'Module::Build::Pluggable::CPANfile';
};

on 'test' => sub {
  requires 'Test::More';
};