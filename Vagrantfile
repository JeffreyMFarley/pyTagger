# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false

  #config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.synced_folder ".", "/home/vagrant"

  config.vm.provider "virtualbox" do |v|
    v.name = "pyTagger"
  end

  config.vm.provision "docker"

  config.vm.provision "shell", inline: "docker build -t app .", run: "always"

  #docker run -it -v /home/vagrant:/home/project app /bin/sh

end
