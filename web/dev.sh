#!/usr/bin/env bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

APPLIBPATH=$SCRIPTPATH/../lib
CARTON_PATH=$SCRIPTPATH/../local/lib/perl5/
PERL5LIB=$APPLIBPATH:$CARTON_PATH:${PERL5LIB}
morbo -w $SCRIPTPATH/validate_metadata.conf -w $SCRIPTPATH/public -w $SCRIPTPATH/templates -w $APPLIBPATH -w $CARTON_PATH $SCRIPTPATH/validate_metadata.pl 
