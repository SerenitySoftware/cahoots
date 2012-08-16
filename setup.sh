#!/bin/bash
cd $(dirname ${BASH_SOURCE[0]})

echo "Installing OS Packages"
apt-get update
apt-get -y upgrade
cat requirements.system | xargs sudo apt-get install -y

echo "Installing required pip Packages"

if [ ! -d ../.env ]
then
	virtualenv ../.env
fi

source ../.env/bin/activate
pip install -r requirements.txt