;NSIS Modern User Interface
;Start Menu Folder Selection Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "TinyERP Client"
  OutFile "tinyerp-client-setup.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\TinyERP Client"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\TinyERP Client" ""

  ;Vista redirects $SMPROGRAMS to all users without this
  RequestExecutionLevel admin

;--------------------------------
;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !define MUI_ICON ".\pixmaps\tinyerp.ico"
  !define MUI_UNICON ".\pixmaps\tinyerp.ico"
  !define MUI_WELCOMEFINISHPAGE_BITMAP ".\pixmaps\tinyerp-intro.bmp"
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP ".\pixmaps\tinyerp-header.bmp"

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "doc\\License.rtf"
 # !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  
  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\TinyERP Client"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "TinyERP Client"
  
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER
  
  !insertmacro MUI_PAGE_INSTFILES

  !define MUI_FINISHPAGE_NOAUTOCLOSE
  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_CHECKED
  !define MUI_FINISHPAGE_RUN_TEXT "Start TinyERP Client"
  !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
  !define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
  !define MUI_FINISHPAGE_SHOWREADME $INSTDIR\README.txt
  !insertmacro MUI_PAGE_FINISH

  
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "TinyERP Client" SecTinyERPClient

  SetOutPath "$INSTDIR"
  
  ;ADD YOUR OWN FILES HERE...
  File /r "dist\\*"

  SetOutPath "$INSTDIR\\GTK"
  File /r "C:\GTK\*"

  SetOutPath "$INSTDIR\\doc"
  File "doc\\*"

  ;Store installation folder
  WriteRegStr HKCU "Software\TinyERP Client" "" $INSTDIR
  
  ;Create uninstaller
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TinyERP Client" "DisplayName" "TinyERP Client (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TinyERP Client" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\TinyERP Client.lnk" "$INSTDIR\tinyerp-client.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;Descriptions

  ;Language strings
  LangString DESC_SecTinyERPClient ${LANG_ENGLISH} "TinyERP Client."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTinyERPClient} $(DESC_SecTinyERPClient)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END
 
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  Push "$INSTDIR\GTK"
  Push ""
  Call un.RmFilesButOne

  Delete "$INSTDIR\matplotlibdata\*"
  Delete "$INSTDIR\pict\*"
  Delete "$INSTDIR\icons\*"
  Delete "$INSTDIR\pict\*"
  Delete "$INSTDIR\po\*"
  Push "$INSTDIR\themes"
  Push ""
  Call un.RmFilesButOne
  Delete "$INSTDIR\doc\*"

  Delete "$INSTDIR\*"

  Delete "$INSTDIR\Uninstall.exe"

  Push "$INSTDIR\GTK"
  Push ""
  Call un.RmDirsButOne
  RMDir "$INSTDIR\GTK"

  RMDir "$INSTDIR\matplotlibdata"
  RMDir "$INSTDIR\pict"
  RMDir "$INSTDIR\icons"
  RMDir "$INSTDIR\po"
  Push "$INSTDIR\themes"
  Push ""
  Call un.RmDirsButOne
  RMDir "$INSTDIR\themes"
  RMDir "$INSTDIR\doc"
  RMDir "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP

  Delete "$SMPROGRAMS\$MUI_TEMP\TinyERP Client.lnk"

  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"

  startMenuDeleteLoop:
    ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."

    IfErrors startMenuDeleteLoopDone

    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TinyERP Client"
  DeleteRegKey /ifempty HKCU "Software\TinyERP Client"

SectionEnd

Function LaunchLink
  ExecShell "" "$INSTDIR\tinyerp-client.exe"
FunctionEnd

Function un.RmDirsButOne
 Exch $R0 ; exclude dir
 Exch
 Exch $R1 ; route dir
 Push $R2
 Push $R3
 
  FindFirst $R3 $R2 "$R1\*.*"
  IfErrors Exit
 
  Top:
   StrCmp $R2 "." Next
   StrCmp $R2 ".." Next
   StrCmp $R2 $R0 Next
   IfFileExists "$R1\$R2\*.*" 0 Next
    RmDir /r "$R1\$R2"
 
   #Goto Exit ;uncomment this to stop it being recursive
 
   Next:
    ClearErrors
    FindNext $R3 $R2
    IfErrors Exit
   Goto Top
 
  Exit:
  FindClose $R3
 
 Pop $R3
 Pop $R2
 Pop $R1
 Pop $R0
FunctionEnd

Function un.RmFilesButOne
 Exch $R0 ; exclude file
 Exch
 Exch $R1 ; route dir
 Push $R2
 Push $R3
 
  FindFirst $R3 $R2 "$R1\*.*"
  IfErrors Exit
 
  Top:
   StrCmp $R2 "." Next
   StrCmp $R2 ".." Next
   StrCmp $R2 $R0 Next
   IfFileExists "$R1\$R2\*.*" Next
    Delete "$R1\$R2"
 
   #Goto Exit ;uncomment this to stop it being recursive
 
   Next:
    ClearErrors
    FindNext $R3 $R2
    IfErrors Exit
   Goto Top
 
  Exit:
  FindClose $R3
 
 Pop $R3
 Pop $R2
 Pop $R1
 Pop $R0
FunctionEnd
