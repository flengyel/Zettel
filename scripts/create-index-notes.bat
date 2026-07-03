@echo off
setlocal EnableExtensions

rem create-index-notes.bat
rem Creates missing reserved alphanumeric index notes for a Zettelkasten vault.
rem Existing files are skipped; this script never overwrites notes.
rem This script creates only the reserved index files; it does not constrain ordinary note IDs.
rem
rem SEE ALSO links use this portable form:
rem   [[ID]]  TITLE
rem with two spaces after the closing double brackets. The emitted line also
rem ends with two spaces so Markdown previewers that follow CommonMark render
rem each SEE ALSO entry on its own line.
rem
rem The master INDEX note links to the subordinate alphanumeric index notes
rem under SEE ALSO. Each subordinate index note links back to INDEX under
rem SEE ALSO.
rem
rem Usage:
rem   create-index-notes.bat
rem   create-index-notes.bat path\to\zettelkasten

set "SP=  "
set "OUTDIR=%~1"
if "%OUTDIR%"=="" set "OUTDIR=."

if not exist "%OUTDIR%\" (
    if exist "%OUTDIR%" (
        >&2 echo Error: output path exists but is not a directory: "%OUTDIR%"
        exit /b 1
    )

    mkdir "%OUTDIR%"
    if errorlevel 1 (
        >&2 echo Error: failed to create output directory "%OUTDIR%"
        exit /b 1
    )
)

call :write_master_index
if errorlevel 1 exit /b 1

call :write_index_note "0000.0000.0ABC" "A-B-C"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0DEF" "D-E-F"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0GHI" "G-H-I"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0JKL" "J-K-L"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0MNO" "M-N-O"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0PQR" "P-Q-R"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0STU" "S-T-U"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0VWX" "V-W-X"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.00YZ" "Y-Z"
if errorlevel 1 exit /b 1
call :write_index_note "0000.0000.0009" "0-9"
if errorlevel 1 exit /b 1

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
    echo(
    echo ## SEE ALSO
    echo(
    echo [[0000.0000.0ABC]]%SP%A-B-C%SP%
    echo [[0000.0000.0DEF]]%SP%D-E-F%SP%
    echo [[0000.0000.0GHI]]%SP%G-H-I%SP%
    echo [[0000.0000.0JKL]]%SP%J-K-L%SP%
    echo [[0000.0000.0MNO]]%SP%M-N-O%SP%
    echo [[0000.0000.0PQR]]%SP%P-Q-R%SP%
    echo [[0000.0000.0STU]]%SP%S-T-U%SP%
    echo [[0000.0000.0VWX]]%SP%V-W-X%SP%
    echo [[0000.0000.00YZ]]%SP%Y-Z%SP%
    echo [[0000.0000.0009]]%SP%0-9%SP%
    echo(
    echo ## References
)
if errorlevel 1 (
    >&2 echo Error: failed to write "%FILE%"
    exit /b 1
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
    echo(
    echo ## SEE ALSO
    echo(
    echo [[0000.0000.0000]]%SP%INDEX%SP%
    echo(
    echo ## References
)
if errorlevel 1 (
    >&2 echo Error: failed to write "%FILE%"
    exit /b 1
)

echo Created "%FILE%"
exit /b 0
