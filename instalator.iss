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
Source: "stawki_nadgodzin.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\start.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SRPANS"; Filename: "{app}\start.bat"
Name: "{commondesktop}\SRPANS"; Filename: "{app}\start.bat"; Tasks: desktopicon
Name: "{userdesktop}\Stawki nadgodzin"; Filename: "{app}\stawki_nadgodzin.csv"

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe skróty:"