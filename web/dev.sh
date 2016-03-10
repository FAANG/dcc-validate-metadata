#!/usr/bin/env bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

APPLIBPATH=$SCRIPTPATH/../lib
PERL5LIB=${PERL5LIB}:$APPLIBPATH
morbo -w $SCRIPTPATH/validate_metadata.conf -w $SCRIPTPATH/public -w $SCRIPTPATH/templates -w $APPLIBPATH $SCRIPTPATH/validate_metadata.pl 
