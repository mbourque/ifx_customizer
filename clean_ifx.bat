@echo off
setlocal

set "BASE=%CD%"

rem 1) Delete *.prt.* in this folder
del /q "%BASE%\*.prt.*" 2>nul

rem 2) Delete trail.txt.* in this folder
del /q "%BASE%\trail.txt.*" 2>nul

rem 3) Delete all files in ifx\parts\ifx_fastener_data
if exist "%BASE%\ifx\parts\ifx_fastener_data" (
    del /q "%BASE%\ifx\parts\ifx_fastener_data\*.*" 2>nul
)

rem 4) Clean ifx\parts\ifx_catalogs, keep only ifx_catalogs.txt
if exist "%BASE%\ifx\parts\ifx_catalogs" (
    pushd "%BASE%\ifx\parts\ifx_catalogs"

    for %%F in (*.*) do (
        if /I not "%%~nxF"=="ifx_catalogs.txt" del "%%F"
    )

    (
        echo #screws
        echo.
        echo #pins
    ) > "ifx_catalogs.txt"

    popd
)

endlocal