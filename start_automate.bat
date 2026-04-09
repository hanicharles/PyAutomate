@echo off
echo =========================================
echo Starting PyAutomate Web Server...
echo =========================================
start "PyAutomate Web Server" cmd /k "python app.py"

echo.
echo =========================================
echo Starting Data Sync in Background...
echo Running sync_google_form.py every 0.5 seconds...
echo =========================================
:sync_loop
python sync_google_form.py
powershell -Command "Start-Sleep -Seconds 0.5"
goto sync_loop
