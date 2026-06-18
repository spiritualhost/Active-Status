# Active Status

Get daily Windows server and workstation activation status in the amount of days remaining for the trial period.

## Compile

The file `active-status.spec` is used to properly link the dlls required by the psycopg2 library.

```powershell
pyinstaller.exe .\active-status.spec
```

## Logs

Logs are sent to the local AppData directory. Most troubleshooting starts there, as the messages from each transmission will be written to `as.log` in that directory. On my Windows 11 installation, the filepath is:

```powershell
C:\Users\{username}\AppData\Local\ActiveStatus\Logs
```
