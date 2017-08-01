#!/bin/bash
set -ex

# packages
sudo apt-get -qq update
sudo apt-get install -y \
   build-essential \
   luajit \
   gambc \
   openjdk-8-jdk-headless \
   ocaml-nox \
   nodejs \
   perl \
   php5-cli \
   ruby \
   rustc

# build isolate
pushd /tmp
git clone --depth=1 https://github.com/ioi/isolate.git
pushd isolate
make PREFIX="/usr" VARPREFIX="/var" CONFIGDIR="/etc" isolate

# install isolate
sudo make PREFIX="/usr" VARPREFIX="/var" CONFIGDIR="/etc" install
popd
popd

# use a non-autistic path
sudo sed -i "s|/var/local/lib/isolate|/var/lib/isolate|" /etc/isolate

# group & setuid stuff
sudo groupadd isolate
sudo usermod -a -G isolate $USER
sudo chown -v root:isolate /usr/bin/isolate
sudo chmod -v u+s /usr/bin/isolate

# pip stuff
pip install -U pip setuptools wheel
