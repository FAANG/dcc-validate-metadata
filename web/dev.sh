#!/usr/bin/env bash
PERL5LIB=${PERL5LIB}:../lib
morbo -w . -w ./public validate_metadata.pl 