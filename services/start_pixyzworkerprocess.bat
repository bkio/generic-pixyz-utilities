@echo off
echo ***************************************
echo ********* Pixyz Worker Process ********
echo ***************************************
echo.
set IS_FILE_WRITE=true
set UPLOAD_HIERARCHY_RAF=c:\\tmp\\test.x3dp_h
set UPLOAD_GEOMETRY_RAF=c:\\tmp\\test.x3dp_g
set UPLOAD_METADATA_RAF=c:\\tmp\\test.x3dp_m
set UPLOAD_HIERARCHY_CF=c:\\tmp\\test.x3dc_h
set UPLOAD_GEOMETRY_CF=c:\\tmp\\test.x3dc_g
set UPLOAD_METADATA_CF=c:\\tmp\\test.x3dc_m
set GOOGLE_PLAIN_CREDENTIALS=none
set GOOGLE_CLOUD_PROJECT_ID=none
set DEPLOYMENT_BUILD_NUMBER=0
set DEPLOYMENT_BRANCH_NAME=development
set PROGRAM_ID=0
set REDIS_ENDPOINT=localhost
set REDIS_PORT=6379
set REDIS_PASSWORD=N/A
set PORT=8081
set CAD_PROCESS_NOTIFY_URL=Value
".\PixyzWorkerProcess\bin\Debug\netcoreapp3.1\PixyzWorkerProcess.exe"
pause