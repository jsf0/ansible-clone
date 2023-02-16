# ansible-clone

This Python script will create an Ansible playbook that duplicates an existing system. The idea is that once you have a system configured the way you like it, you just run this tool and it will create a playbook that you can use to configure another system in the same way.

Currently it only supports FreeBSD and OpenBSD, and is a rough work in progress.

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

Support for new running this on other oeprating systems can be added fairly easily. You will need to modify the following functions: 

`get_installed_packages()`

`get_enabled_services()`

These would need the appropriate commands added to them to grab the list of installed packages and enabled services respectively for the current OS. 
