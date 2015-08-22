def Kernel.is_windows?
    processor, platform, *rest = RUBY_PLATFORM.split("-")
    platform == 'mingw32'
end

Vagrant.configure("2") do |config|

    config.vm.box = "pjcolp/trusty64"
    config.vm.network :public_network, :bridge => ENV['VAGRANT_BRIDGE']
    config.vm.network :forwarded_port, guest: 8000, host: 8000
    config.vm.synced_folder ".", "/vagrant", type: "nfs"
    config.vm.provision :shell, :path => "setup/vagrant_provision.sh"
    config.ssh.username = "vagrant"
    config.ssh.shell = "bash -l"
    config.ssh.keep_alive = true
    config.ssh.forward_agent = true
    config.ssh.forward_x11 = true
    config.vagrant.host = :detect

    config.vm.provider :virtualbox do |virtualbox, override|
        virtualbox.customize ["modifyvm", :id, "--name", "cahoots"]
        virtualbox.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        virtualbox.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        virtualbox.customize ["modifyvm", :id, "--memory", 2048]
    end

    config.vm.provider "hyperv" do |hv|
        hv.memory = 2048
        hv.vmname = 'cahoots'
        hv.cpus = 2
        hv.ip_address_timeout = 300
    end
end
