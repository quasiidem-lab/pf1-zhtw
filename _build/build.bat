@echo off
rem PF1 Foundry zh-TW build. verify must PASS before shipping.
setlocal
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
echo [1/2] build_zhtw.py
python build_zhtw.py || goto fail
echo [2/2] verify_zhtw.py
python verify_zhtw.py || goto fail
echo.
echo Done. audit_all.py is a separate gap report, not part of the build.
goto :eof
:fail
echo.
echo FAILED. Do not ship the output.
exit /b 1