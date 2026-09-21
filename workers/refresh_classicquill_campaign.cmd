@echo off
setlocal
set "URL=https://raw.githubusercontent.com/brianstephanderson-code/anderson-house-test1/main/workers/classicquill_mailbox.py"
set "DEST=C:\AH\BIN\classicquill_mailbox.py"

echo Anderson House - refresh CLASSICQUILL mailbox
powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing '%URL%' -OutFile '%DEST%.new'"
if errorlevel 1 exit /b 1

python -m py_compile "%DEST%.new"
if errorlevel 1 (
  echo New worker failed syntax check. Existing worker left untouched.
  del "%DEST%.new" >nul 2>&1
  exit /b 1
)

copy /Y "%DEST%.new" "%DEST%" >nul
del "%DEST%.new" >nul 2>&1

schtasks /End /TN "AH Classicquill Mailbox" >nul 2>&1
timeout /t 2 /nobreak >nul
schtasks /Run /TN "AH Classicquill Mailbox"

echo DONE - CLASSICQUILL campaign mode refreshed.
endlocal
