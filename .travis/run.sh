#!/bin/bash
set -ex
# run command un virtualenv, under isolate group
sudo -E su $USER -c "cd $TRAVIS_BUILD_DIR; source $VIRTUAL_ENV/bin/activate; $*"
