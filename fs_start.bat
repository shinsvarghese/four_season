:: Run below script from the (root) folder (requires python anaconda 3.5 installation, s. installation howto http://github.conti.de/ADAS-Machine-Learning/redvine/wiki/Installation)

:: This batch file will parse the fs_windows.ini file to get to the correct python path and then run the python script to set up the environment for Redvine

@echo off
:: ---------------------------------------------------------
:: Get the python interpreter configured in the fs_windows.ini using some batch script magic
:: ---------------------------------------------------------

setlocal enabledelayedexpansion
:: Automatically remove the trailing and leading ::spaces from the path given in fs_windows.ini . The key word is case insensitve.
SET key_word="Python"
:: removing the leading and trailing spaces
for /F " eol=# tokens=1,2 delims==" %%G in (fs_windows.ini) do (  
for /f "tokens=* delims= " %%a in ("%%G") do set input=%%a
for /l %%a in (1,1,100) do if "!input:~-1!"==" " set input=!input:~0,-1!

::find the entry corresponding to the key_word (Python)
if  /I  "!input!" ==  %key_word%  set exe=%%H )
:: romoving the leading and trailing spaces
for /f "tokens=* delims= " %%a in ("%exe%") do set input=%%a
for /l %%a in (1,1,200) do if "!input:~-1!"==" " set input=!input:~0,-1!
::removing leading and trailing qoutes 
set input=%input:"=%
set "python_path=%input%\python.exe"

:: ---------------------------------------------------------

:: using  python interpreter specified in fs_winodws.ini file  for the venv setup script
"%python_path%" fs_windows_setup.py venv

:: switch to python environment
call .\env\Scripts\activate.bat

:: install modules, set windows path variable properly and spawn a new cmd window
"%python_path%" fs_windows_setup.py start %1