#!/usr/bin/env bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

PERL5LIB=${PERL5LIB}:$SCRIPTPATH/../lib
morbo -w $SCRIPTPATH/validate_metadata.conf -w $SCRIPTPATH/public $SCRIPTPATH/validate_metadata.pl 