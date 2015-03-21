def Kernel.is_windows?
    processor, platform, *rest = RUBY_PLATFORM.split("-")
    platform == 'mingw32'
end

Vagrant.configure("2") do |config|
    # Standard VM Settings
    config.vm.box = "hashicorp/precise64"

    if Kernel.is_windows?
        config.vm.network :public_network, :bridge => ENV['VAGRANT_BRIDGE']
    elsif ENV['VAGRANT_PRIVATE_IP'].nil?
        config.vm.network :private_network, type: :dhcp
    else
        config.vm.network :private_network, ip: ENV['VAGRANT_PRIVATE_IP']
    end

	config.vm.network :forwarded_port, guest: 8000, host: 8000

    config.vm.synced_folder ".", "/vagrant", type: "nfs"

    # Provisioning
    config.vm.provision :shell, :path => "setup/vagrant_provision.sh"

    # SSH Configuration
    config.ssh.username = "vagrant"
    config.ssh.shell = "bash -l"
    config.ssh.keep_alive = true
    config.ssh.forward_agent = true
    config.ssh.forward_x11 = true
    config.vagrant.host = :detect

    # VirtualBox Provider
    config.vm.provider :virtualbox do |virtualbox, override|
        virtualbox.customize ["modifyvm", :id, "--name", "cahoots"]
        virtualbox.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        virtualbox.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        virtualbox.customize ["modifyvm", :id, "--memory", 2048]
    end

    config.vm.provider "vmware_fusion" do |v|
        v.vmx["memsize"] = "2048"
    end
    config.vm.provider "vmware_desktop" do |v|
        v.vmx["memsize"] = "2048"
    end
    config.vm.provider "vmware_workstation" do |v|
        v.vmx["memsize"] = "2048"
    end
end
