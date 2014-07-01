#!/bin/bash

VERSION=$1

if [ "$VERSION" == "" ] ; then
  echo "usage: $0 <version number>"

  LAST=`ls -1rt _backups/gomh_*.zip`
  echo "  Latest Backup: $LAST"

  exit 1
fi

VERSION_STRING=`printf "%03d" $VERSION`

FILE=_backups/gomh_${VERSION_STRING}.zip

if [ -e $FILE ] ; then
  echo "error: backup file already exists: $FILE"
  exit 1
fi



echo "Created: $FILE"

