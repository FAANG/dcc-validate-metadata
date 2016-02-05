requires 'Moose';
requires 'MooseX::Params::Validate';
requires 'JSON';
requires 'JSON::XS';
requires 'JSON::Validator';
requires 'Data::DPath';
requires 'Scalar::Util';
requires 'Try::Tiny';
requires 'autodie';
requires 'Excel::Writer::XLSX';
requires 'Memoize';
requires 'URI::Escape::XS';
requires 'namespace::autoclean';
requires 'REST::Client';
requires 'JSON::XS';
requires 'XML::Simple';
requires 'URI';
requires 'DateTime::Format::ISO8601';
requires 'Mojolicious', '>= 6.33';
requires 'Mojolicious::Plugin::RenderFile';
requires 'UUID::Generator::PurePerl';
requires 'Spreadsheet::ParseExcel::Stream::XLSX';

on 'build' => sub {
  requires 'Module::Build::Pluggable';
  requires 'Module::Build::Pluggable::CPANfile';
};

on 'test' => sub {
  requires 'Test::More';
};
