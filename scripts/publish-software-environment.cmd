@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish-software-environment.ps1" %*
exit /b %ERRORLEVEL%
