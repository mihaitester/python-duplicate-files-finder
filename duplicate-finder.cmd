@echo off
echo ^>^>^> default use script that will dump the `.cache` file containing metadata and the `.json` file containing duplicates
echo ^>^>^> replace `%*` with a drive path like `c:\` or `d:\` or include both `c:\ d:\` or pass them through the `.cmd` script

set "command=python duplicate-finder.py -j -c %*"
echo %command%
%command%