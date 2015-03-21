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
11. win_inet_pton
12. hiredis
15. LatLon

Contributor Dev Requirements
----------------------------
1. [VirtualBox] (https://www.virtualbox.org/wiki/Downloads) or ([VMWare](http://www.vmware.com/) and [Vagrant VMware Provider](http://www.vagrantup.com/vmware))
2. [Vagrant 1.7+](http://www.vagrantup.com)
3. [Git] (http://git-scm.com/)

Dev VM Setup
------------
1. Clone this repository and `cd` into the clone's directory.
2. Run the command `git submodule update --init`.
3. Run the command `vagrant up` or `vagrant up --provider vmware_workstation` in the clone's root.
4. Wait for provisioning to complete (will take several minutes).

Cahoots Server Setup
--------------------
1. Clone this repository.
2. Enter the directory containing this readme file.
3. Run the command `./setup/server_provision.sh` to install all dependencies and setup cahoots.
4. As a priviledged user: Run the command `nohup ./web/wsgi.py $`
5. To terminate the server: Run the command `killall wsgi.py`

Unit/Flake8/Pylint Test Execution
---------------------------------
1. Run the command `vagrant ssh` to connect to your VM. (Alternative: Use PuTTY with host `127.0.0.1`, port `2222` and username/password `vagrant`.)
2. Run the command `./tests/build.sh` to execute unit/flake8/pylint tests.

Web Interface Usage
-------------------
1. Run the command `vagrant ssh` to connect to your VM. (Alternative: Use PuTTY with host `127.0.0.1`, port `2222` and username/password `vagrant`.)
2. Run the command `./web/wsgi.py` in your VM  to start the Cahoots web interface.
3. Visit `http://localhost:8000` to use the web interface.
4. POST or GET against `http://localhost:8000/api/` using the `q` parameter to retrieve JSON API responses.
