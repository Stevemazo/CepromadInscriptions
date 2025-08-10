[Setup]
AppName=Cepromad Online Register
AppVersion=1.0
DefaultDirName={pf}\CepromadOnlineRegister
DefaultGroupName=CepromadOnlineRegister
OutputDir=.
OutputBaseFilename=CepromadOnlineRegister
Compression=lzma
SolidCompression=yes
SetupIconFile="logo.ico"

[Files]
; L'exécutable principal
Source: "dist\app_gui\app_gui.exe"; DestDir: "{app}"; Flags: ignoreversion

; Tous les fichiers internes (templates, static, DLL, etc.)
Source: "dist\app_gui\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs createallsubdirs ignoreversion

; Le fichier logo
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Raccourci dans le menu Démarrer
Name: "{group}\Application Médicale"; Filename: "{app}\app_gui.exe"; IconFilename: "{app}\logo.ico"

; Raccourci sur le bureau
Name: "{commondesktop}\Cepromad Online Register"; Filename: "{app}\app_gui.exe"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Tasks]
; Option pour créer le raccourci sur le bureau
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Options supplémentaires"

[Run]
; Lancer l'application automatiquement après installation
Filename: "{app}\app_gui.exe"; Description: "Lancer l'application"; Flags: nowait postinstall skipifsilent
