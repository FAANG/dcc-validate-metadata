#!/usr/bin/env bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

APPLIBPATH=$SCRIPTPATH/../lib
CARTON_PATH=$SCRIPTPATH/../local/lib/perl5/
PERL5LIB=$APPLIBPATH:$CARTON_PATH:${PERL5LIB}
perl -d:NYTProf $SCRIPTPATH/validate_metadata.pl daemon
