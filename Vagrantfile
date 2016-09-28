# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false

  config.vm.network "private_network", ip: "192.168.50.20"

  config.vm.synced_folder ".", "/home/vagrant"

  config.vm.provider "virtualbox" do |v|
    v.name = "pyTagger"
    v.memory = 2000
    v.cpus = 2
  end

  config.vm.provision "docker"

end
