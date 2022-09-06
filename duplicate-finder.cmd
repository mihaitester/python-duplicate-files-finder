rem default use script that will dump the `.cache` file containing metadata and the `.json` file containing duplicates
rem replace `%*` with a drive path like `c:\` or `d:\` or include both `c:\ d:\` or pass them through the `.cmd` script
python duplicate-finder.py -j -c %*