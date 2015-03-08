#!/bin/bash

cd /vagrant

echo " "
echo "Beginning Provisioning!"
echo "Please ignore any 'stdin' related errors. It's an Ubuntu+Vagrant bug."
echo " "


echo "Step 1: Adding APT Repositories and Updating APT"
wget http://download.logilab.org/production/logilab-dists-key.asc
apt-key add logilab-dists-key.asc
rm logilab-dists-key.asc
add-apt-repository "deb http://download.logilab.org/production precise/"
apt-get update > /dev/null

echo "Step 2: Upgrading Base System Packages"
apt-get -y upgrade > /dev/null

echo "Step 3: Installing Required System Packages"
cat setup/requirements.system.txt | xargs apt-get install -y --force-yes > /dev/null

echo "Step 4: Installing Required Python Packages"
pip install -r setup/requirements.txt > /dev/null

echo "Step 5: Installing Development Python Packages"
pip install -r setup/requirements.dev.txt > /dev/null

echo "Step 6: Moving files around"
echo 'cd /vagrant' >> /home/vagrant/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:/vagrant' >> /home/vagrant/.bashrc

echo " "
echo " "
echo "Provisioning Complete!"
echo " "
echo "Instructions for web client:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './web/wsgi.py' to start Cahoots."