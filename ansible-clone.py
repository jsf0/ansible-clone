#!/usr/bin/env python3

import argparse
import configparser
import os
import distro
import subprocess
import textwrap

def get_become_method():
    if distro.id() == 'openbsd':
        return "doas"
    else:
        return "sudo"

def get_installed_packages():
    # Get a list of installed packages. Only including manually installed, not dependencies
    if distro.id() == 'freebsd':
        result = subprocess.run(['pkg', 'query', '-e', '%#r = 0', '%n'], capture_output=True, text=True)
    elif distro.id() == 'openbsd':
        result = subprocess.run(['pkg_info', '-q', '-m', '-z'], capture_output=True, text=True) 

    return [line.split(' ')[0] for line in result.stdout.splitlines()]

def generate_package_tasks(installed_packages):
    # Generate a task to install the specified packages. Ansible will choose the package manager
    ansible_pkg_mgr = 'ansible.builtin.package'
    package_tasks = []
    package_tasks.append(f"- name: Install packages\n      {ansible_pkg_mgr}:\n        name:\n")
    for package in installed_packages:
        package_tasks.append(f"        - {package}\n")
    package_tasks.append(f"       state: present\n")
    return ' '.join(package_tasks)

def read_config_files(config_paths):
    # Read configuration files from the .ini file.
    config = configparser.ConfigParser()
    config.read(config_paths)
    return config

def generate_config_tasks(config):
    # Generate a task to copy the specified config files to their paths.
    tasks = []
    for section in config.sections():
        file_path = os.path.expanduser(config[section]['path'])
        with open(file_path) as f:
            content = f.read()
        # Escape the file content using YAML block scalar style
        escaped_content = textwrap.indent(content, ' ' * 10)
        task = f"    - name: Copy {file_path}\n" \
               f"      copy:\n" \
               f"        dest: {file_path}\n" \
               f"        content: |\n" \
               f"{escaped_content}\n"
        tasks.append(task)
    return tasks

def get_enabled_services():
    # Find enabled services. Note that this will find ALL enabled services, including default ones
    if distro.id() == 'freebsd':
        output = subprocess.check_output(['service', '-e'])

    elif distro.id() == 'openbsd':
        output = subprocess.check_output(['rcctl', 'ls', 'on'])

    # Convert the output to a string and split it into lines
    output_str = output.decode('utf-8')
    lines = output_str.split('\n')

    # Filter out any empty lines and parse the service names
    services = [line.split()[0] for line in lines if line.strip()]

    # Strip the "/etc/rc.d/" prefix from the service names (needed for FreeBSD)
    return [s.replace('/etc/rc.d/', '') for s in services]

def generate_service_tasks(enabled_services):
    # Generate a list of Ansible tasks to enable the specified services.
    service_tasks = []
    for service in enabled_services:
        service_tasks.append(f"    - name: Enable {service} service\n      service:\n        name: {service}\n        enabled: yes\n")
    return service_tasks


def generate_playbook(config_paths, playbook_out):
    # Generate the Ansible playbook.
    become_method = get_become_method()

    installed_packages = get_installed_packages()
    package_tasks = generate_package_tasks(installed_packages)

    config = read_config_files(config_paths)
    config_tasks = generate_config_tasks(config)

    enabled_services = get_enabled_services()
    service_tasks = generate_service_tasks(enabled_services)

    with open(playbook_out, 'w') as f:
        f.write(f'''---
- hosts: localhost
  become: yes
  become_method: {become_method}

  tasks:
    {package_tasks}
{''.join(config_tasks)}
{''.join(service_tasks)}
''')

def main():
    # Will eventually want to make these arguments optional

    parser = argparse.ArgumentParser(description='Options for ansible-clone')
    parser.add_argument('-c', dest='config_paths', required=True, type=str, help='INI file containing config file paths')
    parser.add_argument('-f', dest='output_file', required=True, type=str, help='Output playbook file')

    args = parser.parse_args()

    generate_playbook(args.config_paths, args.output_file)

if __name__ == '__main__':
    main()
