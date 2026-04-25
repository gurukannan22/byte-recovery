@echo off
echo Installing required packages...
pip install eel pyinstaller

echo.
echo Building Byte Recovery Executable...
pyinstaller app.py --noconsole --onefile --name "ByteRecoveryPro" --add-data "web;web"

echo.
echo Build Complete!
echo You can find your executable in the 'dist' folder.
pause
