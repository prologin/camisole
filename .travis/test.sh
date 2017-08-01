#!/bin/bash
set -ex

# safety check
if ! [[ $(sudo -E su $USER -c 'groups') == *isolate* ]]; then
   echo "$USER is not in isolate group"
   exit 1;
fi

# setup.py test, under isolate group
sudo -E su $USER -c \
"cd $TRAVIS_BUILD_DIR;"\
"source $VIRTUAL_ENV/bin/activate;"\
"which python; python --version;"\
"python setup.py test"
