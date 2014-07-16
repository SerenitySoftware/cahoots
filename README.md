Cahoots
=======
A Text Comprehension Engine in Python
=====================================

Project State
-------------
```
Pre-Alpha / System Testing
```

Demo
----
[rwven.com:8000] (http://rwven.com:8000) (API is disabled, and queries are limited to 256 bytes)

Contributors
------------
1. [Jordan Ambra] (https://github.com/jordanambra)
2. [Ryan Vennell] (https://github.com/hickeroar)

Requirements
------------
1. python-dev
2. python-pip
3. redis-server
4. Python Packages:

    ```
    flask
    mako
    dateutils
    pyyaml
    pygments
    pyparsing
    redisbayes
    phonenumbers
    simplejson
    hiredis (optional)
    ```

Contributor Dev Requirements
----------------------------
1. [VirtualBox] (https://www.virtualbox.org/wiki/Downloads) (Alternative: [VMWare](http://www.vmware.com/) and [Vagrant VMware provider](http://www.vagrantup.com/vmware))
2. [Vagrant 1.6+](http://www.vagrantup.com)
3. [Git] (http://git-scm.com/)

Setup
-----
1. Clone this repository.
2. Run vagrant up: `vagrant up` or `vagrant up --provider vmware_workstation` in the clone's root.

    ```
    $ vagrant up --provider vmware_workstation
    Bringing machine 'default' up with 'vmware_workstation' provider...
    ==> default: Cloning VMware VM: 'hashicorp/precise64'. This can take some time...
    ==> default: Checking if box 'hashicorp/precise64' is up to date...
    ==> default: Verifying vmnet devices are healthy...
    ==> default: Preparing network adapters...
    ==> default: Starting the VMware VM...
    ==> default: Waiting for the VM to finish booting...
    ==> default: The machine is booted and ready!
    ==> default: Forwarding ports...
        default: -- 8000 => 8000
        default: -- 22 => 2222
    ==> default: Configuring network adapters within the VM...
    ==> default: Waiting for HGFS kernel module to load...
    ==> default: Enabling and configuring shared folders...
        default: -- X:/Documents/cahoots: /vagrant
    ==> default: Running provisioner: shell...
        default: Running: C:/Users/FooBar/AppData/Local/Temp/vagrant-shell20140715-6492-12sh4x2.sh
    
    NOTE: Provisioning will continue here and output updates to the screen
    ```

3. Type `vagrant ssh` to connect to your vm. (Alternative: Use PuTTY with host `127.0.0.1`, port `2222` and username/password `vagrant`.)
4. Type `./wsgi.py`  to start Cahoots.
5. Visit `http://localhost:8000` to view the web interface.