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

  ;Store installation folder
  WriteRegStr HKCU "Software\TinyERP Client" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\TinyERP Client.lnk" "$INSTDIR\tinyerp-client.exe"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
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
  Delete "$INSTDIR\GTK\bin\*"
  Delete "$INSTDIR\GTK\etc\fonts\conf.avail\*"
  Delete "$INSTDIR\GTK\etc\fonts\conf.d\*"
  Delete "$INSTDIR\GTK\etc\fonts\gtk-2.0\*"
  Delete "$INSTDIR\GTK\etc\fonts\pango\*"
  Delete "$INSTDIR\GTK\etc\fonts\*"
  Delete "$INSTDIR\GTK\etc\gtk-2.0\*"
  Delete "$INSTDIR\GTK\etc\pango\*"
  Delete "$INSTDIR\GTK\etc\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.4.0\engines\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.4.0\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\engines\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\immodules\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\loaders\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\*"
  Delete "$INSTDIR\GTK\lib\gtk-2.0\*"
  Delete "$INSTDIR\GTK\lib\libglade\2.0\*"
  Delete "$INSTDIR\GTK\lib\libglade\*"
  Delete "$INSTDIR\GTK\lib\pango\1.6.0\modules\*"
  Delete "$INSTDIR\GTK\lib\pango\1.6.0\*"
  Delete "$INSTDIR\GTK\lib\pango\*"
  Delete "$INSTDIR\GTK\lib\*"
  Delete "$INSTDIR\GTK\share\gtk-2.0\demo\*"
  Delete "$INSTDIR\GTK\share\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\gtkthemeselector\pixmaps\*"
  Delete "$INSTDIR\GTK\share\gtkthemeselector\*"
  Push "$INSTDIR\GTK\share\locale"
  Push ""
  Call un.RmFilesButOne
  Delete "$INSTDIR\GTK\share\themes\Default\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\Default\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\Default\*"
  Delete "$INSTDIR\GTK\share\themes\Emacs\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\Emacs\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\Emacs\*"
  Delete "$INSTDIR\GTK\share\themes\Metal\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\Metal\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\Metal\*"
  Delete "$INSTDIR\GTK\share\themes\MS-Windows\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\MS-Windows\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\MS-Windows\*"
  Delete "$INSTDIR\GTK\share\themes\Raleigh\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\Raleigh\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\Raleigh\*"
  Delete "$INSTDIR\GTK\share\themes\Redmond95\gtk-2.0-key\*"
  Delete "$INSTDIR\GTK\share\themes\Redmond95\gtk-2.0\*"
  Delete "$INSTDIR\GTK\share\themes\Redmond95\*"
  Delete "$INSTDIR\GTK\share\themes\*"
  Delete "$INSTDIR\GTK\share\xml\libglade\*"
  Delete "$INSTDIR\GTK\share\xml\*"
  Delete "$INSTDIR\GTK\share\*"
  Delete "$INSTDIR\GTK\*"

  Delete "$INSTDIR\matplotlibdata\*"
  Delete "$INSTDIR\pict\*"
  Delete "$INSTDIR\icons\*"
  Delete "$INSTDIR\pict\*"
  Delete "$INSTDIR\po\*"
  Delete "$INSTDIR\themes\Aquativo\*"
  Delete "$INSTDIR\themes\YattaBlues\icons\*"
  Delete "$INSTDIR\themes\YattaBlues\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\16x16\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\16x16\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\22x22\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\22x22\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\32x32\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\32x32\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\apps\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\devices\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\emblems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\filesystems2\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\mimetypes\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\64x64\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\64x64\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72\devices\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96\devices\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\128x128\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\128x128\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\192x192\filesystems\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\192x192\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\Yattacier3\*"
  Delete "$INSTDIR\themes\Yattacier3\icons\*"
  Delete "$INSTDIR\themes\Yattacier3\other\*"
  Delete "$INSTDIR\themes\Yattacier3\*"
  Delete "$INSTDIR\themes\*"
  Delete "$INSTDIR\*"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR\GTK\bin"
  RMDir "$INSTDIR\GTK\etc\fonts\conf.avail"
  RMDir "$INSTDIR\GTK\etc\fonts\conf.d"
  RMDir "$INSTDIR\GTK\etc\fonts\gtk-2.0"
  RMDir "$INSTDIR\GTK\etc\fonts\pango"
  RMDir "$INSTDIR\GTK\etc\fonts"
  RMDir "$INSTDIR\GTK\etc\gtk-2.0"
  RMDir "$INSTDIR\GTK\etc\pango"
  RMDir "$INSTDIR\GTK\etc"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.4.0\engines"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.4.0"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\engines"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\immodules"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.10.0\loaders"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0\2.10.0"
  RMDir "$INSTDIR\GTK\lib\gtk-2.0"
  RMDir "$INSTDIR\GTK\lib\libglade\2.0"
  RMDir "$INSTDIR\GTK\lib\libglade"
  RMDir "$INSTDIR\GTK\lib\pango\1.6.0\modules"
  RMDir "$INSTDIR\GTK\lib\pango\1.6.0"
  RMDir "$INSTDIR\GTK\lib\pango"
  RMDir "$INSTDIR\GTK\lib"
  RMDir "$INSTDIR\GTK\share\gtk-2.0\demo"
  RMDir "$INSTDIR\GTK\share\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\gtkthemeselector\pixmaps"
  RMDir "$INSTDIR\GTK\share\gtkthemeselector"
  Push "$INSTDIR\GTK\share\locale"
  Push ""
  Call un.RmDirsButOne
  RMDir "$INSTDIR\GTK\share\locale"
  RMDir "$INSTDIR\GTK\share\themes\Default\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\Default\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\Default"
  RMDir "$INSTDIR\GTK\share\themes\Emacs\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\Emacs\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\Emacs"
  RMDir "$INSTDIR\GTK\share\themes\Metal\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\Metal\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\Metal"
  RMDir "$INSTDIR\GTK\share\themes\MS-Windows\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\MS-Windows\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\MS-Windows"
  RMDir "$INSTDIR\GTK\share\themes\Raleigh\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\Raleigh\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\Raleigh"
  RMDir "$INSTDIR\GTK\share\themes\Redmond95\gtk-2.0-key"
  RMDir "$INSTDIR\GTK\share\themes\Redmond95\gtk-2.0"
  RMDir "$INSTDIR\GTK\share\themes\Redmond95"
  RMDir "$INSTDIR\GTK\share\themes"
  RMDir "$INSTDIR\GTK\share\xml\libglade"
  RMDir "$INSTDIR\GTK\share\xml"
  RMDir "$INSTDIR\GTK\share"
  RMDir "$INSTDIR\GTK"

  RMDir "$INSTDIR\matplotlibdata"
  RMDir "$INSTDIR\pict"
  RMDir "$INSTDIR\icons"
  RMDir "$INSTDIR\po"
  RMDir "$INSTDIR\themes\Aquativo"
  RMDir "$INSTDIR\themes\YattaBlues"
  RMDir "$INSTDIR\themes\YattaBlues\icons"
  RMDir "$INSTDIR\themes\YattaBlues"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\16x16\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\16x16"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\22x22\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\22x22"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\32x32\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\32x32"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\apps"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\devices"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\emblems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\filesystems2"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48\mimetypes"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\48x48"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\64x64\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\64x64"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72\devices"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\72x72"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96\devices"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\96x96"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\128x128\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\128x128"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\192x192\filesystems"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3\192x192"
  RMDir "$INSTDIR\themes\Yattacier3\icons\Yattacier3"
  RMDir "$INSTDIR\themes\Yattacier3\icons"
  RMDir "$INSTDIR\themes\Yattacier3\other"
  RMDir "$INSTDIR\themes\Yattacier3"
  RMDir "$INSTDIR\themes"
  RMDir "$INSTDIR"
  
  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
  Delete "$SMPROGRAMS\$MUI_TEMP\TinyERP Client.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall.lnk"
  
  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"
 
  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."
    
    IfErrors startMenuDeleteLoopDone
  
    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

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
