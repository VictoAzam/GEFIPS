; Script de instalador Inno Setup para GEFIPS
; Gere antes o executável com PyInstaller em dist/GEFIPS

[Setup]
AppName=GEFIPS
AppVersion=2.0.0
AppPublisher=GEFIPS
DefaultDirName={pf}\GEFIPS
DefaultGroupName=GEFIPS
OutputBaseFilename=GEFIPS-Setup-v2.0
ArchitecturesInstallIn64BitMode=x64
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\GEFIPS.exe
VersionInfoVersion=2.0.0
VersionInfoCompany=GEFIPS
VersionInfoDescription=Sistema de Gestão Financeira Pessoal
WizardImageFile=..\logo\Gemini_Generated_Image_vwaqrtvwaqrtvwaq(1).png
WizardSmallImageFile=..\logo\Gemini_Generated_Image_vwaqrtvwaqrtvwaq(1).png

[Files]
Source: "..\dist\GEFIPS\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\GEFIPS"; Filename: "{app}\GEFIPS.exe"
Name: "{autodesktop}\GEFIPS"; Filename: "{app}\GEFIPS.exe"

[Run]
Filename: "{app}\GEFIPS.exe"; Description: "Executar GEFIPS"; Flags: nowait postinstall skipifsilent
