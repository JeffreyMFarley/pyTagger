# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false

  config.vm.network "forwarded_port", guest: 9200, host: 9200

  config.vm.synced_folder ".", "/home/vagrant"

  config.vm.provider "virtualbox" do |v|
    v.name = "pyTagger"
    v.memory = 2000
    v.cpus = 2
  end

  config.vm.provision "docker"

end
