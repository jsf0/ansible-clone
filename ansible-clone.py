#!/usr/bin/env python3.9

import configparser
import os
import distro
import subprocess
import textwrap

def get_installed_packages():
    # Get a list of installed packages using the specified package manager.
    if distro.id() == 'freebsd':
        result = subprocess.run(['pkg', 'query', '-e', '%#r = 0', '%n'], capture_output=True, text=True)
    return [line.split(' ')[0] for line in result.stdout.splitlines()]

def generate_package_tasks(installed_packages):
    # Generate a list of Ansible tasks to install the specified packages.
    ansible_pkg_mgr = 'ansible.builtin.package'
    package_tasks = []
    package_tasks.append(f"- name: Install packages\n      {ansible_pkg_mgr}:\n        name:\n")
    for package in installed_packages:
        package_tasks.append(f"        - {package}\n")
    package_tasks.append(f"       state: present\n")
    return ' '.join(package_tasks)

def read_config_files():
    # Read configuration files from the .ini file.
    config = configparser.ConfigParser()
    config.read('config_files.ini')
    return config

def generate_config_tasks(config):
    # Generate a list of Ansible tasks to copy the specified config files.
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
    # Find enabled services and ensure the playbook enables them
    if distro.id() == 'freebsd':
        output = subprocess.check_output(['service', '-e'])

        # Convert the output to a string and split it into lines
        output_str = output.decode('utf-8')
        lines = output_str.split('\n')

        # Filter out any empty lines and parse the service names
        services = [line.split()[0] for line in lines if line.strip()]

        # Strip the "/etc/rc.d/" prefix from the service names
        return [s.replace('/etc/rc.d/', '') for s in services]

def generate_service_tasks(enabled_services):
    """Generate a list of Ansible tasks to enable the specified services."""
    service_tasks = []
    for service in enabled_services:
        service_tasks.append(f"    - name: Enable {service} service\n      service:\n        name: {service}\n        enabled: yes\n")
    return service_tasks


def generate_playbook():
    # Generate the Ansible playbook.
    installed_packages = get_installed_packages()
    package_tasks = generate_package_tasks(installed_packages)

    config = read_config_files()
    config_tasks = generate_config_tasks(config)

    enabled_services = get_enabled_services()
    service_tasks = generate_service_tasks(enabled_services)

    with open('playbook.yml', 'w') as f:
        f.write(f'''---
- hosts: localhost
  become: yes

  tasks:
    {package_tasks}
{''.join(config_tasks)}
{''.join(service_tasks)}
''')

def main():
    # The main function.
    generate_playbook()

if __name__ == '__main__':
    main()
