# Client

Resources for the client setup are stored in this folder.

## Compile

The file `active-status.spec` is used to properly link the dlls required by the psycopg2 library.

```powershell
pyinstaller.exe .\active-status.spec
```

This daemon is currently compatible with Windows systems.

## PostgreSQL

Each client daemon will write to a network PostgreSQL server determined by the information provided in a `.env` file so the corresponding server daemon has accurate data to send daily emails. The .env file will look like this:

```shell
DATABASE="{database name}"
USER="{write only username}"
PASSWORD="{write only user's password}"
HOST="{IP address for PostgreSQL server}"
PORT="{server port, default is usually 5432}"
```

The machines do not need to be domain joined, just on the same network as the SQL server. Much of this credential information will be found when initially setting up the SQL server and additional details on setup can be found [on the serverside README](../server/SERVER.md).

## Logs

Logs are sent to the local AppData directory. Most troubleshooting starts there, as the messages from each transmission will be written to `as.log` in that directory. On my Windows 11 installation, the filepath is:

```powershell
C:\Users\{username}\AppData\Local\ActiveStatus\Logs
```
