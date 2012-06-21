#!/bin/bash
cd $(dirname ${BASH_SOURCE[0]})

echo "Installing OS Packages"
cat requirements.system | xargs sudo apt-get install -y

echo "Installing pip Packages"
pip install -r requirements.pip