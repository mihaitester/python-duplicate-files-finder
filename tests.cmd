@echo off

rem echo ">>>" also prints the quotes - making me think that my [cmd.exe] is hacked
echo ^>^>^> Use "tests.cmd --verbose" to get more details
echo ^>^>^> Use "tests.cmd <class_name>.<test_name>" to run singular test. Example "tests.cmd TestDuplicateFinder_SingleThread.test_100_files_random_duplicate"

set "command=rmdir /q /s scrap_test_folder"
echo ^>^>^> %command%
%command%

set "command=python tests.py %*"
echo ^>^>^> %command%
%command%