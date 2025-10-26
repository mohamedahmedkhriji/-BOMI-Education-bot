@echo off
echo Installing BOMI Bot as Windows Service...

sc create "BOMI_Bot" binPath= "python.exe %~dp0start_bot.py" start= auto
sc description "BOMI_Bot" "BOMI DTM Education Bot Service"
sc start "BOMI_Bot"

echo Service installed and started!
pause