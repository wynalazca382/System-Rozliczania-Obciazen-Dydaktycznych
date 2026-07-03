[Setup]
AppName=System Rozliczania Pensum ANS Elblag
AppVersion=1.4
DefaultDirName={pf}\SRPANS
DefaultGroupName=SRPANS
OutputDir=instalator
OutputBaseFilename=SRPSetup
Compression=lzma
SolidCompression=yes
DisableDirPage=yes

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.prod"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.test"; DestDir: "{app}"; Flags: ignoreversion
Source: "stawki_nadgodzin.xlsx"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "spinner.gif"; DestDir: "{app}"; Flags: ignoreversion
Source: "success.gif"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\System Rozliczania Pensum"; Filename: "{app}\app.exe"
Name: "{commondesktop}\SRPANS\System Rozliczania Pensum (Produkcja)"; Filename: "{app}\app.exe"; Tasks: desktopicon
Name: "{commondesktop}\SRPANS\System Rozliczania Pensum (Test)"; Filename: "{app}\app.exe"; Parameters: "--env test"; Tasks: desktopicon
Name: "{commondesktop}\SRPANS\Stawki nadgodzin"; Filename: "{app}\stawki_nadgodzin.xlsx"

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikony na pulpicie"; GroupDescription: "Dodatkowe skróty:"

[Code]
function InitializeSetup(): Boolean;
var
  UninstallPath: string;
  ResultCode: Integer;
begin
  Result := True;

  if RegQueryStringValue(HKLM, 'C:\Program Files (x86)\SRPANS\unins000.exe', 'UninstallString', UninstallPath) then
  begin
    if Exec(UninstallPath, '/VERYSILENT /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
    end
    else
    begin
      MsgBox('Nie udało się uruchomić odinstalatora starej wersji.', mbError, MB_OK);
      Result := False;
    end;
  end
  else
  begin
  end;
end;