Cahoots
=======
A Text Comprehension Engine in Python
-------------------------------------

Status
------
```
Alpha, Accepting Contributions
```
[![Build Status](https://travis-ci.org/SerenitySoftwareLLC/cahoots.svg?branch=master)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/coverage-100%-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/pylint-10.00/10-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/flake8-passing-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)

Contributors
------------
1. [Jordan Ambra] (https://github.com/jordanambra)
2. [Ryan Vennell] (https://github.com/hickeroar)

Software Requirements
---------------------
1. python-dev
2. python-pip
3. sqlite3

Python Package Requirements
---------------------------
1. flask
2. mako
3. dateutils
4. pyyaml
5. pygments
6. pyparsing
7. simplebayes
8. phonenumbers
9. simplejson
10. SereneRegistry
11. LatLon

Dev Linux Setup / Usage / Requirements
------------------------------
1. Required: This assumes you are developing on a modern linux installation such as Ubuntu 14.10, etc.
2. Clone this repository.
3. Enter the directory containing this readme file.
4. Run the command `sudo ./setup/dev_provision.sh` to install all dependencies and setup cahoots.
5. Run the command `./web/server.py` to start the web interface/api.
6. Visit `http://localhost:8000/` to use the web interface.
7. POST or GET against `http://localhost:8000/api/` using the `q` parameter to retrieve JSON API responses.
9. Run the command `./tests/build.sh` to execute unit/flake8/pylint tests.

Dev VM Setup / Usage / Requirements
---------------------------
1. Required: [VirtualBox] (https://www.virtualbox.org/wiki/Downloads) or ([VMWare](http://www.vmware.com/) and [Vagrant VMware Provider](http://www.vagrantup.com/vmware))
2. Required: [Vagrant 1.7+](http://www.vagrantup.com)
3. Clone this repository and `cd` into the clone's directory.
5. Run the command `vagrant up` or `vagrant up --provider vmware_workstation` in the clone's root.
6. Wait for provisioning to complete (will take several minutes).
7. Run the command `vagrant ssh` to connect to your VM. (Alternative: Use PuTTY with host `127.0.0.1`, port `2222` and username/password `vagrant`.)
8. Run the command `./web/server.py` to start the web interface/api.
9. Visit `http://localhost:8000/` to use the web interface.
10. POST or GET against `http://localhost:8000/api/` using the `q` parameter to retrieve JSON API responses.
11. Run the command `./tests/build.sh` to execute unit/flake8/pylint tests.

Cahoots Server Setup
--------------------
1. Clone this repository.
2. Enter the directory containing this readme file.
3. Run the command `sudo ./setup/server_provision.sh` to install all dependencies and setup cahoots.
4. Run the command `nohup ./web/server.py $` to start the web interface/api.
5. To terminate the server: Run the command `killall server.py`
6. Note: You can change the port the server runs on in /web/config.py. Some ports (ex: 80) require a privileged user.
