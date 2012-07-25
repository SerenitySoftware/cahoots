#!/bin/bash
cd $(dirname ${BASH_SOURCE[0]})

echo "Installing OS Packages"
apt-get update
apt-get -y upgrade
cat requirements.system | xargs sudo apt-get install -y

echo "Installing required pip Packages"
sudo pip install -r requirements.pip

echo "Installing optional pip Packages"
sudo pip install -r optional.pip