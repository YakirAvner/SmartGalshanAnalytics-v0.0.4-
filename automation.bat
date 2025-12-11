@echo off
cd /d "%~dp0SG-Analytics"
call ..\\hy.venv\\Scripts\\activate.bat

REM Start all devices in parallel (separate Python processes for maximum speed)
start /b python main.py --device_IP SG23=2.54.238.136:51807
start /b python main.py --device_IP SG25=2.54.88.254:51807
start /b python main.py --device_IP SG26=2.54.89.1:51807

REM Uncomment below for additional devices
REM start /b python main.py --device_IP SG9=2.54.238.146:51807
REM start /b python main.py --device_IP SG20=109.253.65.75:51807
REM start /b python main.py --device_IP SG21=2.54.89.11:51807

echo All devices started in parallel!
pause