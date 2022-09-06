rem default use script that will dump the `.cache` file containing metadata and the `.json` file containing duplicates
rem replace `"%cd%"` with a drive path like `c:\` or `d:\` or include both `c:\ d:\`
python duplicate-finder.py -j -c "%cd%"