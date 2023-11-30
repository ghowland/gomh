#!/bin/bash

VERSION=$1

if [ "$VERSION" == "" ] ; then
  echo "usage: $0 <version number>"

  LAST=`ls -1rtd _backups/gomh_* | tail -1`
  echo "  Latest Backup: $LAST"

  exit 1
fi

VERSION_STRING=`printf "%03d" $VERSION`

DIR=_backups/gomh_${VERSION_STRING}

if [ -d $DIR ] ; then
  echo "error: backup dir already exists: $DIR"
  exit 1
fi

mkdir $DIR
cp *.py $DIR

echo "Created: $DIR"

