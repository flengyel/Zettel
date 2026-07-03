@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish-software-inventory.ps1" %*
exit /b %ERRORLEVEL%
