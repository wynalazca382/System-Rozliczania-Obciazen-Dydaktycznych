[Setup]
AppName=System Rozliczania Pensum ANS Elblag
AppVersion=1.0
DefaultDirName={pf}\SRPANS
DefaultGroupName=SRPANS
OutputDir=instalator
OutputBaseFilename=SRPSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\instantclient_23_7\*"; DestDir: "{app}\instantclient_23_7"; Flags: recursesubdirs

[Icons]
Name: "{group}\SRPANS"; Filename: "{app}\app.exe"
Name: "{commondesktop}\SRPANS"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe skróty:"

[Run]
Filename: "{cmd}"; Parameters: "/C setx PATH ""{app}\instantclient_19_11;%PATH%"""; Flags: runhidden

[Registry] 
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "PATH"; ValueData: "{app}\instantclient_19_11;%PATH%";