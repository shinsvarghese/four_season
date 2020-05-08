@echo off

set CYGWIN=nodosfilewarning

pushd "%~dp0cntlmRunDir"

::  :: Run proxy with password hash from config file, stored like this:
::  ::   Username   uidg6XXX
::  ::   ...
::  ::   # ------------------------------------------------
::  ::   Auth            NTLMv2
::  ::   PassNTLMv2      BC145608XXXXXXXXXXXXXXXXXXXX9297
::  ::   # ------------------------------------------------
::  "%~dp0cntlm\cntlm.exe" -f -c "%~dp0cntlm\cntlm.ini"

:: Do not load password hash from config file, but ask interactively instead.
:: Use the "%USERNAME%" environment variable to determine the username.
echo.
echo Starting proxy for user "%USERNAME%"...
echo.
"%~dp0cntlm\cntlm.exe" -f -c "%~dp0cntlm\cntlm.ini" -I -u %USERNAME%

popd

pause
