#!/bin/bash

cd /vagrant

echo " "
echo "Beginning Provisioning!"
echo "Please ignore any 'stdin' related errors. It's an Ubuntu+Vagrant bug."

echo " "
echo " [Cahoots] Step 1: Adding APT Repositories and Updating APT"
echo " "
apt-get update -o Acquire::ForceIPv4=true

echo " "
echo " [Cahoots] Step 2: Upgrading Base System Packages"
echo " "
apt-get upgrade -y --force-yes -o Acquire::ForceIPv4=true

echo " "
echo " [Cahoots] Step 3: Installing Required System Packages"
echo " "
cat setup/requirements.system.txt | xargs apt-get install -y --force-yes -o Acquire::ForceIPv4=true

echo " "
echo " [Cahoots] Step 4: Installing Required Python Packages"
echo " "
pip install -r setup/requirements.txt

echo " "
echo " [Cahoots] Step 5: Installing Development Python Packages"
echo " "
pip install -r setup/requirements.dev.txt

echo " "
echo " [Cahoots] Step 6: Importing Location Database"
echo " "
cp cahoots/parsers/location/data/location.sqlite.dist cahoots/parsers/location/data/location.sqlite
bzip2 -d -k cahoots/parsers/location/data/city.txt.bz2
cat cahoots/parsers/location/data/city.sql | sqlite3 cahoots/parsers/location/data/location.sqlite
rm cahoots/parsers/location/data/city.txt
bzip2 -d -k cahoots/parsers/location/data/country.csv.bz2
cat cahoots/parsers/location/data/country.sql | sqlite3 cahoots/parsers/location/data/location.sqlite
rm cahoots/parsers/location/data/country.csv
bzip2 -d -k cahoots/parsers/location/data/street_suffix.csv.bz2
cat cahoots/parsers/location/data/street_suffix.sql | sqlite3 cahoots/parsers/location/data/location.sqlite
rm cahoots/parsers/location/data/street_suffix.csv
bzip2 -d -k cahoots/parsers/location/data/landmark.csv.bz2
cat cahoots/parsers/location/data/landmark.sql | sqlite3 cahoots/parsers/location/data/location.sqlite
rm cahoots/parsers/location/data/landmark.csv

echo " "
echo " [Cahoots] Step 7: Setting Up Bash Defaults"
cat /vagrant/setup/bashrc >> /home/vagrant/.bashrc

echo " "
echo " "
echo "Provisioning Complete!"
echo " "
echo "Instructions for web client:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './cahootserver/server.py' to start Cahoots."
echo " "
echo "Instructions for unit/pylint/flake8 tests:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './tests/build.sh' to execute the test suite."
