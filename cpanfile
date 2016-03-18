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
requires 'Spreadsheet::ParseXLSX';
requires 'Cache::LRU';
requires 'LWP::UserAgent';
requires 'XML::LibXML';
requires 'Text::Unidecode';
requires 'Unicode::CaseFold';
requires 'MooseX::Types::URI';

on 'build' => sub {
  requires 'Module::Build::Pluggable';
  requires 'Module::Build::Pluggable::CPANfile';
};

on 'test' => sub {
  requires 'Test::More';
};
