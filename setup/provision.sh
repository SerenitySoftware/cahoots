#!/bin/bash

cd /vagrant

echo " "
echo "Beginning Provisioning!"
echo "Please ignore any 'stdin' related errors. It's an Ubuntu+Vagrant bug."

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
echo " [Cahoots] Step 5: Installing Development Python Packages"
echo " "
pip install -r setup/requirements.dev.txt
cd ~/
wget https://pypi.python.org/packages/source/p/pylint/pylint-1.4.1.tar.gz
tar -xvf pylint-1.4.1.tar.gz
cd pylint-1.4.1
python setup.py install
cd ..
rm -rf pylint-1.4.1
rm -f pylint-1.4.1.tar.gz

echo " "
echo " [Cahoots] Step 6: Moving files around"
echo 'cd /vagrant' >> /home/vagrant/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:/vagrant' >> /home/vagrant/.bashrc

echo " "
echo " "
echo "Provisioning Complete!"
echo " "
echo "Instructions for web client:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './web/wsgi.py' to start Cahoots."
echo " "
echo "Instructions for unit/pylint/flake8 tests:"
echo "1) Type 'vagrant ssh' to connect to your vm."
echo "2) Type './tests/vagrant_build.sh' to execute the test suite."
