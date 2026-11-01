; Script de instalador Inno Setup para Calculator Fan Desktop (Windows 10/11 x64)
#define MyAppName "Calculator Fan"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Calculator Fan Team"
#define MyAppURL "https://github.com/calculator-fan"
#define MyAppExeName "calculator_fan.exe"

[Setup]
AppId={{E57D2C04-D72D-4C67-B02F-4A9B8D8F7B39}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=CalculatorFan_Setup_x64
SetupIconFile=assets\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\calculator_fan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\app_icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Verificação do Microsoft Edge WebView2 Evergreen Runtime
function IsWebView2Installed(): Boolean;
var
  VersionStr: String;
  GuidKey: String;
begin
  GuidKey := 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  Result := False;

  // Verifica HKLM 64-bit
  if RegQueryStringValue(HKLM64, GuidKey, 'pv', VersionStr) and (VersionStr <> '') and (VersionStr <> '0.0.0.0') then
  begin
    Result := True;
    Exit;
  end;

  // Verifica HKLM 32-bit (caso instalado em modo 32-bit no Windows 64-bit)
  if RegQueryStringValue(HKLM32, GuidKey, 'pv', VersionStr) and (VersionStr <> '') and (VersionStr <> '0.0.0.0') then
  begin
    Result := True;
    Exit;
  end;

  // Verifica HKCU (instalação por usuário)
  if RegQueryStringValue(HKCU, GuidKey, 'pv', VersionStr) and (VersionStr <> '') and (VersionStr <> '0.0.0.0') then
  begin
    Result := True;
    Exit;
  end;
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  if not IsWebView2Installed() then
  begin
    if MsgBox('O Microsoft Edge WebView2 Runtime não foi detectado no sistema.' + #13#10 +
              'O Calculator Fan requer o WebView2 para renderizar sua interface gráfica nativa.' + #13#10#13#10 +
              'Deseja abrir a página oficial de download da Microsoft agora?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://go.microsoft.com/fwlink/p/?LinkId=2124703', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    end;
  end;
end;
