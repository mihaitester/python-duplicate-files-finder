@echo off

set "command=rmdir /q /s scrap_test_folder"
echo ^>^>^> %command%
%command%

set "command=python tests.py %*"
echo ^>^>^> %command%
%command%