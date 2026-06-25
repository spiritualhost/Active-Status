; Active Status Server Daemon - Inno Setup Script
; Non-commercial use only

#define MyAppName "Active Status Server Daemon"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Ryan Piazza"
#define MyAppExeName "active-status-daemon.exe"
#define MyAppDataDir "ThresholdNotifications (ActiveStatus)"

[Setup]
AppId={{CC1E2D5E-6F84-46F5-9797-73565FC8A569}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputBaseFilename=active-status-server-daemon-setup
SetupIconFile=assets\w98_magnifying_glass.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  CredentialsPage: TInputFileWizardPage;

procedure InitializeWizard();
begin
  CredentialsPage := CreateInputFilePage(
    wpWelcome,
    'Import Credentials',
    'Select your .env credentials file',
    'Credentials file (.env):'
  );
  CredentialsPage.Add(
    '',
    'Environment files|*.env|All files|*.*',
    '.env'
  );
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = CredentialsPage.ID then
  begin
    if CredentialsPage.Values[0] = '' then
    begin
      MsgBox('Please select a credentials file before continuing.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  SourceFile, DataDir, ConfigPath, TaskFile, TaskXML: String;
  ResultCode: Integer;
  TaskExists: Boolean;
begin
  if CurStep = ssPostInstall then
  begin
    // ProgramData dir - writable by both SYSTEM and interactive users
    DataDir := ExpandConstant('{commonappdata}\{#MyAppDataDir}');
    ForceDirectories(DataDir);
    ForceDirectories(DataDir + '\Config');

    // Copy .env to the data dir root so load_dotenv() finds it
    // when WorkingDirectory is set to DataDir in the scheduled task
    SourceFile := CredentialsPage.Values[0];
    if SourceFile <> '' then
      FileCopy(SourceFile, DataDir + '\.env', False);

    // config.ini path - matches what the Python script constructs via PROGRAMDATA
    ConfigPath := DataDir + '\Config\config.ini';

    // Check if the scheduled task already exists
    TaskExists := False;
    Exec('schtasks.exe', '/Query /TN "Active Status"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    if ResultCode = 0 then
      TaskExists := True;

    if TaskExists then
    begin
      if MsgBox('A scheduled task named "Active Status" already exists. Overwrite it?',
        mbConfirmation, MB_YESNO) = IDNO then
      begin
        Exit;
      end;
    end;

    // Build the scheduled task XML
    // Runs daily at 17:00 as SYSTEM regardless of whether a user is logged in
    TaskXML :=
      '<?xml version="1.0" encoding="UTF-16"?>' +
      '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">' +
        '<Triggers>' +
          '<CalendarTrigger>' +
            '<StartBoundary>2024-01-01T17:00:00</StartBoundary>' +
            '<ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>' +
          '</CalendarTrigger>' +
        '</Triggers>' +
        '<Principals>' +
          '<Principal id="Author">' +
            '<UserId>S-1-5-18</UserId>' +
            '<RunLevel>HighestAvailable</RunLevel>' +
          '</Principal>' +
        '</Principals>' +
        '<Settings>' +
          '<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>' +
          '<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>' +
          '<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>' +
          '<ExecutionTimeLimit>PT1H</ExecutionTimeLimit>' +
          '<Enabled>true</Enabled>' +
        '</Settings>' +
        '<Actions>' +
          '<Exec>' +
            '<Command>"' + ExpandConstant('{app}\{#MyAppExeName}') + '"</Command>' +
            '<Arguments>--db_check --config "' + ConfigPath + '"</Arguments>' +
            '<WorkingDirectory>' + DataDir + '</WorkingDirectory>' +
          '</Exec>' +
        '</Actions>' +
      '</Task>';

    // Write XML to a temp file, register the task, then clean up
    TaskFile := ExpandConstant('{tmp}\active_status_task.xml');
    SaveStringToFile(TaskFile, TaskXML, False);

    Exec('schtasks.exe',
      '/Create /TN "Active Status" /XML "' + TaskFile + '" /F',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    DeleteFile(TaskFile);

    if ResultCode <> 0 then
      MsgBox(
        'Warning: scheduled task registration failed (schtasks exit code: ' +
        IntToStr(ResultCode) + ').' + #13#10 +
        'The application was installed successfully, but the daily scan will not run automatically. ' +
        'You may need to register the task manually.',
        mbError, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Remove the scheduled task
    Exec('schtasks.exe',
      '/Delete /TN "Active Status" /F',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Remove the app install directory
    DelTree(ExpandConstant('{app}'), True, True, True);

    // Remove the ProgramData directory (config.ini, .env, logs etc.)
    DelTree(ExpandConstant('{commonappdata}\{#MyAppDataDir}'), True, True, True);
  end;
end;
