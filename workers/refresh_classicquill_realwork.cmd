@echo off
setlocal
set "BASE=https://raw.githubusercontent.com/brianstephanderson-code/anderson-house-test1/main/workers"
set "DIR=C:\AH\MAILROOM\workers"

echo Refreshing CLASSICQUILL real-work mode...
powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing '%BASE%/classicquill_mailbox.py' -OutFile '%DIR%\classicquill_mailbox.py.new'; Invoke-WebRequest -UseBasicParsing '%BASE%/classicquill_policy_audit.py' -OutFile '%DIR%\classicquill_policy_audit.py.new'"
if errorlevel 1 exit /b 1

"C:\Program Files\Python313\python.exe" -m py_compile "%DIR%\classicquill_mailbox.py.new" "%DIR%\classicquill_policy_audit.py.new"
if errorlevel 1 (
  echo Syntax check failed. Existing files left untouched.
  del "%DIR%\classicquill_mailbox.py.new" >nul 2>&1
  del "%DIR%\classicquill_policy_audit.py.new" >nul 2>&1
  exit /b 1
)

copy /Y "%DIR%\classicquill_mailbox.py.new" "%DIR%\classicquill_mailbox.py" >nul
copy /Y "%DIR%\classicquill_policy_audit.py.new" "%DIR%\classicquill_policy_audit.py" >nul
del "%DIR%\classicquill_mailbox.py.new" >nul 2>&1
del "%DIR%\classicquill_policy_audit.py.new" >nul 2>&1

schtasks /End /TN "AH Classicquill Mailbox" >nul 2>&1
timeout /t 2 /nobreak >nul
schtasks /Run /TN "AH Classicquill Mailbox"
timeout /t 2 /nobreak >nul
schtasks /Query /TN "AH Classicquill Mailbox" /FO LIST | findstr Status
echo DONE - real-work mode installed.
pause
