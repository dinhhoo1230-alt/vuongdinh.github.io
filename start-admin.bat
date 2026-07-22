@echo off
REM ================================================
REM  Mo cong cu Admin quan ly du an (portfolio)
REM  Bam dup file nay de bat dau.
REM ================================================
cd /d "%~dp0"
echo Dang khoi dong cong cu Admin...
start "Admin Server - DUNG DONG CUA SO NAY" py admin_server.py
timeout /t 2 >nul
start "" http://localhost:8001/admin.html
echo.
echo Da mo trinh duyet tai http://localhost:8001/admin.html
echo De cua so den "Admin Server" MO trong luc lam viec.
echo Xong viec thi dong cua so den do lai la duoc.
timeout /t 4 >nul
