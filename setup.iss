[Setup]
AppName=Gerador de Nota Fiscal DANFE
AppVersion=1.0
AppPublisher=Seu Nome ou Empresa
DefaultDirName={autopf}\Gerador DANFE
DefaultGroupName=Gerador DANFE
OutputDir=C:\temp
OutputBaseFilename=Instalador_Gerador_DANFE
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Gerador_DANFE.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icone.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Gerador DANFE"; Filename: "{app}\Gerador_DANFE.exe"
Name: "{autodesktop}\Gerador DANFE"; Filename: "{app}\Gerador_DANFE.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Gerador_DANFE.exe"; Description: "{cm:LaunchProgram,Gerador DANFE}"; Flags: nowait postinstall skipifsilent
