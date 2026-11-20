# Server

Resources for serverside setup are going to be located in this folder.

## Email Daemon

Enter a destination email and a threshold in days for notification.

A `.env` file will be necessary to complete the reads from the SQL table. The `.env` will need to be structured like this:

```shell
DATABASE="active_status"
USER="read_only"
PASSWORD="{read only user's password}"
HOST="{IP address for PostgreSQL server}"
PORT=5432
```

SMTP server credentials are necessary to the performance of the daemon, so they will be entered when the GUI is launched -- do this by doubleclicking on the exe (the GUI will also launch via the command line and if a config file doesn't exist).

Launch a database scan with the settings specified in the config file with:

```powershell
python.exe .\server_daemon.py --db_check
```

Or similarly with the compiled executable.

On Fedora, perform a scan and email with 

The daemon expects explicit TLS, so a TLS port should be specified for the SMTP server. It is recommended to set up 2FA or MFA on whichever SMTP account is used, given the method of credential storage (this can be improved in the future).

## PostgreSQL

In order for the email daemon to function properly, a PostgreSQL server will need to be set up to store client transmission data. Client daemons periodically send a heartbeat to the SQL server with their activation countdown and the email daemon will read from there daily, at the predetermined schedule, to send out an email via the set SMTP server.

PostgreSQL can be [downloaded from their page here](https://www.postgresql.org/download/).

### Installation

#### Fedora

```bash
#Set up SQL
sudo chmod +x ./setup-sql/fedora.sh
sudo ./setup-sql/fedora.sh
```

The database name is set to `active_status` in the above script. Passwords are set for all three necessary users as well, but they are weak passwords and should be changed. It is recommended to do this automatically, previous to dispersing the `.env` files.

The server email daemon doesn't necessarily need to be on the same machine (it can even run on a Windows machine if preferred) to give users the flexibility to centralize their SQL setup. Run the following to set up a daily scan and email blast:

```bash
...
```

**Cron script to come**

## Compile

The file `active-status-daemon.spec` is used to properly link the dlls required by the `psycopg2` library.

```powershell
pyinstaller.exe .\active-status-daemon.spec
```

If compiling for a Fedora system, first install the following development libraries to properly build the `psycopg2` library from source:

```bash
sudo dnf install libpq-devel python3-devel gcc
```

Test an email by running the script once to set up SMTP, then running again with the --db_check flag:

```bash
sudo ./active-status-daemon
sudo ./active-status-daemon --db_check
```
