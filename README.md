# ansible-clone

This Python script will create an Ansible playbook that duplicates an existing Linux or BSD system. The idea is that once you have a system configured the way you like it, you just run this tool and it will create a playbook that you can use to configure another system in the same way.

Currently it supports generating playbooks on the following operating systems:

 - OpenBSD
 - FreeBSD
 - Debian
 - Ubuntu
 - Linux Mint
 - Arch Linux
 - CentOS
 - Fedora
 - RHEL


### usage

This will load the file `config_file_paths.ini` and include the contents of all the config files found there in the playbook. The playbook will be written to `playbook.yml`
```
ansible-clone -c config_file_paths.ini -f playbook.yml
```

The file `config_file_paths.ini` here should look something like this:

```
[spectrwm.conf]
path = /home/joe/.spectrwm.conf

[pf.conf]
path = /etc/pf.conf
```
The contents of the files at these paths will be included in the resulting playbook.

### Supporting new operating systems

Support for new running this on other operating systems can be added fairly easily. You will need to modify the following functions: 

`get_installed_packages()`

`get_enabled_services()`


### TODO

- [ ] Write a man page
- [ ] Fix all the roff formatting in that man page that I will have messed up the first time
- [ ] Add some command line flags to optionally disable each function (e.g, ignore packages, services, or config files)
- [X] Implement support for Linux. Will need to include various package managers, and systemctl to grab service info
- [ ] Add support for including variables such as IP address, hostname, etc. 
- [ ] Add a Makefile
