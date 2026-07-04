@echo off
setlocal EnableExtensions

rem create-index-notes.bat
rem Creates missing reserved alphanumeric index notes for a Zettelkasten vault.
rem Existing files are skipped; this script never overwrites notes.
rem This script creates only the reserved index files; it does not constrain ordinary note IDs.
rem
rem SEE ALSO links keep the target as an ID-only WikiLink and place the
rem title after it as plain text:
rem   [[ID]] TITLE
rem
rem The master INDEX note links to the subordinate alphanumeric index notes
rem under SEE ALSO. Each subordinate index note links back to INDEX under
rem SEE ALSO.
rem
rem Usage:
rem   create-index-notes.bat
rem   create-index-notes.bat path\to\zettelkasten

set "SEP= "
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
    echo [[0000.0000.0ABC]]%SEP%A-B-C
    echo [[0000.0000.0DEF]]%SEP%D-E-F
    echo [[0000.0000.0GHI]]%SEP%G-H-I
    echo [[0000.0000.0JKL]]%SEP%J-K-L
    echo [[0000.0000.0MNO]]%SEP%M-N-O
    echo [[0000.0000.0PQR]]%SEP%P-Q-R
    echo [[0000.0000.0STU]]%SEP%S-T-U
    echo [[0000.0000.0VWX]]%SEP%V-W-X
    echo [[0000.0000.00YZ]]%SEP%Y-Z
    echo [[0000.0000.0009]]%SEP%0-9
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
    echo [[0000.0000.0000]]%SEP%INDEX
    echo(
    echo ## References
)
if errorlevel 1 (
    >&2 echo Error: failed to write "%FILE%"
    exit /b 1
)

echo Created "%FILE%"
exit /b 0
