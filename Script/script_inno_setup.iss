; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "CustodiaTech"
#define MyAppVersion "1.6"
#define MyAppPublisher "MPRN"
#define MyAppURL "https://www.mprn.mp.br/"
#define MyAppExeName "interface_projeto_captura.exe"
#define MyAppAssocName MyAppName + ""
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
; Para ID dinâmico, usar: AppId={{MyAppID-{#SetupSetting("AppVersion")}}}
AppId={{F423F459-B701-4FF6-BCDC-882ECC0246FB}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DisableDirPage=yes
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputBaseFilename=CustodiaTech_Setup
SetupIconFile=C:\Users\2050765\Documents\Custodia Tech Dev\ct\imagens\iconecustodiatech.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\2050765\Documents\Custodia Tech Dev\ct\dist\interface_projeto_captura\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\2050765\Documents\Custodia Tech Dev\ct\dist\interface_projeto_captura\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
; Adiciona a entrada no "Adicionar e Remover Programas" com ícone correto
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; \
    ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; \
    ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; \
    ValueType: string; ValueName: "UninstallString"; ValueData: """{uninstallexe}"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{cmd}"; Parameters: "/c attrib +h ""{app}\_internal\.env"""; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

;Garante a remoção tanto dos arquivos quanto dos diretórios dentro de app.
[UninstallDelete]
Type: filesandordirs; Name: "{app}"

;Remove diretórios persistentes
[Code]
procedure DeleteEmptyDir(Path: String);
begin
  if DirExists(Path) then
  begin
    try
      Log('Tentando remover o diretório: ' + Path);
      DelTree(Path, True, True, True);
      Log('Diretório removido com sucesso: ' + Path);
    except
      Log('Erro ao remover o diretório: ' + Path);
    end;
  end
  else
    Log('Diretório não encontrado (já pode ter sido removido): ' + Path);
end;

function IsEmptyDir(Dir: string): Boolean;
var
  FindRec: TFindRec;
  Found: Boolean;
begin
  Found := FindFirst(Dir + '\*', FindRec);
  while Found do
  begin
    // Ignora "." e ".."
    if (FindRec.Name <> '.') and (FindRec.Name <> '..') then
    begin
      Result := False;
      Exit;
    end;
    Found := FindNext(FindRec);
  end;
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if DirExists(ExpandConstant('{app}')) and IsEmptyDir(ExpandConstant('{app}')) then
      DeleteEmptyDir(ExpandConstant('{app}'));
  end;
end;