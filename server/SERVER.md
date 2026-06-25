# Server

Resources for serverside setup are going to be located in this folder.

## Email Daemon

Enter a destination email and a threshold in days for notification.

A `.env` file will be necessary to complete the reads from the SQL table. The `.env` will need to be structured like this:

```shell
DATABASE="{database name}"
USER="{read only username}"
PASSWORD="{read only user's password}"
HOST="{IP address for host}"
PORT="{server port, default is usually 5432}"
```

SMTP server credentials are necessary to the performance of the daemon, so they will be entered when the GUI is launched -- do this by doubleclicking on the exe (the GUI will also launch via the command line and if a config file doesn't exist).

Launch a database scan with the settings specified in the config file with:

```powershell
python.exe .\server_daemon.py --db_check
```

Or similarly with the compiled executable.

The daemon expects explicit TLS, so a TLS port should be specified for the SMTP server. It is recommended to set up 2FA or MFA on whichever SMTP account is used, given the method of credential storage (this can be improved in the future).

## Compile

The file `active-status-daemon.spec` is used to properly link the dlls required by the psycopg2 library.

```powershell
pyinstaller.exe .\active-status-daemon.spec
```
