@echo off

rem echo ">>>" also prints the quotes - making me think that my [cmd.exe] is hacked
echo ^>^>^> Use tests.cmd --verbose to get more details

set "command=rmdir /q /s scrap_test_folder"
echo ^>^>^> %command%
%command%

set "command=python tests.py %*"
echo ^>^>^> %command%
%command%