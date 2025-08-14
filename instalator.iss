[Setup]
AppName=System Rozliczania Pensum ANS Elblag
AppVersion=1.3.1
DefaultDirName={pf}\SRPANS
DefaultGroupName=SRPANS
OutputDir=instalator
OutputBaseFilename=SRPSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.prod"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.test"; DestDir: "{app}"; Flags: ignoreversion
Source: "stawki_nadgodzin.xlsx"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\System Rozliczania Pensum"; Filename: "{app}\app.exe"
Name: "{commondesktop}\System Rozliczania Pensum (Produkcja)"; Filename: "{app}\app.exe"; Tasks: desktopicon
Name: "{commondesktop}\System Rozliczania Pensum (Test)"; Filename: "{app}\app.exe"; Parameters: "--env test"; Tasks: desktopicon
Name: "{userdesktop}\Stawki nadgodzin"; Filename: "{app}\stawki_nadgodzin.xlsx"

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikony na pulpicie"; GroupDescription: "Dodatkowe skróty:"