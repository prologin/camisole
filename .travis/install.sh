#!/bin/bash
set -ex

# ppa for g++ with C++14
sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 1397BC53640DB551
sudo add-apt-repository --yes ppa:ubuntu-toolchain-r/test

# packages
sudo apt-get -qq update
sudo apt-get install -qq -y \
   libcap-dev \
   build-essential g++-6 \
   fp-compiler \
   gambc \
   ghc-dynamic \
   gnat-6 \
   golang-go \
   lua5.2 \
   mono-runtime mono-mcs \
   nodejs \
   ocaml-nox \
   openjdk-8-jdk-headless \
   perl \
   php-cli \
   ruby \
   rustc \
   swi-prolog-nox \
   scala

# dlang
wget -O /tmp/dmd_2.078.2-0_amd64.deb http://downloads.dlang.org/releases/2.x/2.078.2/dmd_2.078.2-0_amd64.deb
sudo dpkg -i /tmp/dmd_2.078.2-0_amd64.deb
dmd --version | head -1

# update-alternatives nonsense to force gcc-6
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 100
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 100
sudo update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 30
sudo update-alternatives --install /usr/bin/cc cc /usr/bin/gcc 30
sudo update-alternatives --set gcc /usr/bin/gcc-6
sudo update-alternatives --set g++ /usr/bin/g++-6
sudo update-alternatives --set c++ /usr/bin/g++
sudo update-alternatives --set cc /usr/bin/gcc
# update-alternatives for node -> nodejs
sudo update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10


# checks
gcc --version | head -1
g++ --version | head -1

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
