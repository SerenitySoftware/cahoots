#!/bin/bash

cd /vagrant

echo " "
echo "Beginning Provisioning!"

echo " "
echo " [Cahoots] Step 1: Adding APT Repositories and Updating APT"
echo " "
apt-get update

echo " "
echo " [Cahoots] Step 2: Upgrading Base System Packages"
echo " "
apt-get -y upgrade

echo " "
echo " [Cahoots] Step 3: Installing Required System Packages"
echo " "
cat setup/requirements.system.txt | xargs apt-get install -y --force-yes

echo " "
echo " [Cahoots] Step 4: Installing Required Python Packages"
echo " "
pip install -r setup/requirements.txt

echo " "
echo " [Cahoots] Step 5: Importing Location Database"
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

echo " "
echo "Provisioning Complete!"
echo "Ensure you have added this directory to the PYTHONPATH"
echo " "
