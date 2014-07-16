#!/bin/bash

cd /vagrant

echo " "
echo "Beginning Provisioning!"
echo "Please ignore any 'stdin' related errors. It's an Ubuntu+Vagrant bug."
echo " "

echo "Step 1: Updating APT"
apt-get update > /dev/null

echo "Step 2: Upgrading Base System Packages"
apt-get -y upgrade > /dev/null

echo "Step 3: Installing Required System Packages"
cat setup/requirements.system | xargs apt-get install -y > /dev/null

echo "Step 4: Installing Required Python Packages"
pip install -r setup/requirements.txt > /dev/null

echo "Step 5: Moving files around"
echo "cd /vagrant" >> /home/vagrant/.bashrc

echo " "
echo " "
echo "Provisioning Complete!"
echo " "
echo "Instructions:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './wsgi.py' to start Cahoots."
echo "3) ???"
echo "4) Profit!"