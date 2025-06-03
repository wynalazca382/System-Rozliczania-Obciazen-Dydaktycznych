[Setup]
AppName=System Rozliczania Pensum ANS Elblag
AppVersion=1.0
DefaultDirName={pf}\SRPANS
DefaultGroupName=SRPANS
OutputDir=instalator
OutputBaseFilename=SRPSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=app\icon.ico

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\start.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\instantclient_23_7\*"; DestDir: "{app}\instantclient_23_7"; Flags: recursesubdirs
Source: "app\icon.ico"; DestDir: "{app}";

[Icons]
Name: "{group}\SRPANS"; Filename: "{app}\start.bat"
Name: "{commondesktop}\SRPANS"; Filename: "{app}\start.bat"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe skróty:"