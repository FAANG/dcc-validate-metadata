requires 'Moose';
requires 'MooseX::Params::Validate';
requires 'JSON';
requires 'JSON::XS';
requires 'JSON::Validator';
requires 'Scalar::Util';

on 'build' => sub {
  requires 'Module::Build::Pluggable';
  requires 'Module::Build::Pluggable::CPANfile';
};

on 'test' => sub {
  requires 'Test::More';
};
