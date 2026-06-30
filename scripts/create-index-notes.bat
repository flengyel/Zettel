@echo off
setlocal EnableExtensions

rem create-basic-index-pages.bat
rem Creates the reserved alphanumeric index notes for the Zettel repository.
rem Usage:
rem   create-basic-index-pages.bat
rem   create-basic-index-pages.bat path\to\zettelkasten

set "OUTDIR=%~1"
if "%OUTDIR%"=="" set "OUTDIR=."

if not exist "%OUTDIR%" (
    mkdir "%OUTDIR%"
)

call :write_master_index

call :write_index_note "0000.0000.0ABC" "A-B-C"
call :write_index_note "0000.0000.0DEF" "D-E-F"
call :write_index_note "0000.0000.0GHI" "G-H-I"
call :write_index_note "0000.0000.0JKL" "J-K-L"
call :write_index_note "0000.0000.0MNO" "M-N-O"
call :write_index_note "0000.0000.0PQR" "P-Q-R"
call :write_index_note "0000.0000.0STU" "S-T-U"
call :write_index_note "0000.0000.0VWX" "V-W-X"
call :write_index_note "0000.0000.00YZ" "Y-Z"
call :write_index_note "0000.0000.0009" "0-9"

echo Done.
exit /b 0

:write_master_index
set "ID=0000.0000.0000"
set "TITLE=INDEX"
set "FILE=%OUTDIR%\%ID%.md"

if exist "%FILE%" (
    echo Skipping existing "%FILE%"
    exit /b 0
)

> "%FILE%" (
    echo ---
    echo id: %ID%
    echo title: %ID% %TITLE%
    echo reference-section-title: References
    echo ---
    echo # %TITLE%
    echo.
    echo ## SEE ALSO
    echo.
    echo [[0000.0000.0ABC^|A-B-C]]
    echo [[0000.0000.0DEF^|D-E-F]]
    echo [[0000.0000.0GHI^|G-H-I]]
    echo [[0000.0000.0JKL^|J-K-L]]
    echo [[0000.0000.0MNO^|M-N-O]]
    echo [[0000.0000.0PQR^|P-Q-R]]
    echo [[0000.0000.0STU^|S-T-U]]
    echo [[0000.0000.0VWX^|V-W-X]]
    echo [[0000.0000.00YZ^|Y-Z]]
    echo [[0000.0000.0009^|0-9]]
    echo.
    echo ## References
)

echo Created "%FILE%"
exit /b 0

:write_index_note
set "ID=%~1"
set "TITLE=%~2"
set "FILE=%OUTDIR%\%ID%.md"

if exist "%FILE%" (
    echo Skipping existing "%FILE%"
    exit /b 0
)

> "%FILE%" (
    echo ---
    echo id: %ID%
    echo title: %ID% %TITLE%
    echo reference-section-title: References
    echo ---
    echo # %TITLE%
    echo.
    echo ## SEE ALSO
    echo.
    echo [[0000.0000.0000^|INDEX]]
    echo.
    echo ## References
)

echo Created "%FILE%"
exit /b 0
