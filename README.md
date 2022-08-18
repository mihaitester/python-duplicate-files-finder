# Readme
I have been trying to make some backup system and after a while ended with a lot of duplicate files that end up taking up space.
So I thought about this tool that would help me find out which files are duplicates and ideally remove the duplicates and put some link to the original file thus saving space and allowing for more backups to be stored on a single HDD.

# Usage
> duplicate-finder.py [path1] [path2] ... -j -e -n

* `-j` - dump a file containing a json with list of sequences of duplicates, where the first element in each list is the original file found, and all successive ones are duplicates
* `-e` - flag indicating that duplicate files should be erased
* `-n` - flag indicating that python should search hidden folders and files including files and folders starting with `.`

