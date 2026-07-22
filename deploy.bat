@echo off
REM ================================================
REM  Dang cac thay doi len web that (GitHub Pages)
REM  Bam dup file nay, roi lam theo huong dan tren man hinh.
REM ================================================
cd /d "%~dp0"
py deploy.py
echo.
echo === Da xong. Doc ky dong chu phia tren. ===
pause
