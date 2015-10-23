requires 'Moose';
requires 'MooseX::Params::Validate';
requires 'JSON';
recommends 'JSON::XS';
requires 'JSON::Validator';
requires 'Data::DPath';
requires 'Scalar::Util';
requires 'Try::Tiny';
requires 'autodie';
requires 'Excel::Writer::XLSX';
requires 'Memoize';
requires 'URI::Escape::XS';
requires 'namespace::autoclean';

on 'build' => sub {
  requires 'Module::Build::Pluggable';
  requires 'Module::Build::Pluggable::CPANfile';
};

on 'test' => sub {
  requires 'Test::More';
};