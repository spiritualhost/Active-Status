# Server

Resources for serverside setup are going to be located in this folder.

## Email Daemon

Enter a destination email and a threshold in days for notification.

A `.env` file will be necessary to complete the reads from the SQL table. The `.env` will need to be structured like this:

```shell
DATABASE="{database name}"
USER="{read only username}"
PASSWORD="{read only user's password}"
HOST="{IP address for PostgreSQL server}"
PORT="{server port, default is usually 5432}"
```

SMTP server credentials are necessary to the performance of the daemon, so they will be entered when the GUI is launched -- do this by doubleclicking on the exe (the GUI will also launch via the command line and if a config file doesn't exist).

Launch a database scan with the settings specified in the config file with:

```powershell
python.exe .\server_daemon.py --db_check
```

Or similarly with the compiled executable.

The daemon expects explicit TLS, so a TLS port should be specified for the SMTP server. It is recommended to set up 2FA or MFA on whichever SMTP account is used, given the method of credential storage (this can be improved in the future).

## PostgreSQL

In order for the email daemon to function properly, a PostgreSQL server will need to be set up to store client transmission data. Client daemons periodically send a heartbeat to the SQL server with their activation countdown and the email daemon will read from there daily, at the predetermined schedule, to send out an email via the set SMTP server.

PostgreSQL can be [downloaded from their page here](https://www.postgresql.org/download/).

### Installation

#### Ansible

Community Ansible was used for our setup to provision the PostgreSQL server. [Instructions for setup are located here](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html?extIdCarryOver=true&percmp=RHCTG0260000490184&sc_cid=RHCTG0180000382536).

*Although it is possible to use the control node (the management computer) as the managed node (the target server) to keep hypervisor footprint low by specifying localhost, this risks the "it works on my computer" problem and is not recommended. Even a separate TTY linux environment will be more reliable.*

```bash
[ Control Node ]  --- (Sends instructions via SSH) --->  [ Managed Node ]
(Where Ansible is                                         (The server being configured; 
 installed & run)                                         PostgreSQL gets installed here)
```

Ansible is agentless, so nothing needs to be installed on the production machines reporting to the central SQL server. The control node server will need Python installed, but if it's a Linux server it's likely already there; it will also need the applicable winrm and chocolatey tools (the requirements can also be installed from the included `requirements.yaml` file).

```bash
ansible-galaxy collection install -r collections/requirements.yaml
```

The Windows server will [need winrm enabled](https://docs.ansible.com/projects/ansible/latest/os_guide/windows_winrm.html#windows-winrm) and [will need to install chocolatey](https://docs.chocolatey.org/en-us/choco/setup/#install-with-powershell.exe).

Once Ansible has been installed on the control node of choice, we'll be ready to run the `postgresql.yaml` playbook and get the server set up.

1) Create an inventory file `inventory.ini` in the below format and add the IP address of the desired Windows server

```ini
[postgres]
192.168.1.50

[postgres:vars]
ansible_connection=winrm
ansible_port=5985
ansible_winrm_scheme=http
ansible_winrm_transport=ntlm
ansible_user=youradmin
```

*Much of this is defaults and SHOULD be changed later.*

2) Target the postgres inventory source from the command line using the provided playbook

```bash
ansible-playbook -i inventory.ini postgresql.yml -k
```

*The --check flag at the end of the command will allow you to see the impact on the servers prior to actually applying them.*

## Compile

The file `active-status-daemon.spec` is used to properly link the dlls required by the psycopg2 library.

```powershell
pyinstaller.exe .\active-status-daemon.spec
```

This daemon is currently compatible with Windows systems.
