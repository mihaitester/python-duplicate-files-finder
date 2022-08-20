# Readme
I have been trying to make some backup system and after a while ended with a lot of duplicate files that end up taking up space.
So I thought about this tool that would help me find out which files are duplicates and ideally remove the duplicates and put some link to the original file thus saving space and allowing for more backups to be stored on a single HDD.

For example processing `15K` files which take up `212GB` HDD takes roughly `40 minutes` to process the hashes, but the overall duplicate identification takes `10 seconds` iterating over a metadata that is less than `100KB` in RAM. 

# Usage
> duplicate-finder.py [path1] [path2] ... -j -l -e -n

* `-j` - flag indicating the creation of a dump a file containing a json with list of sequences of duplicates, where the first element in each sequence is the original file found, and all successive ones are duplicates, format `[[original_file, duplicate1, dulicate2, ...], ...]`
* `-l` - flag indicating if backlinks from the duplicates to the original file found should be created
* `-e` - flag indicating that duplicate files should be erased
* `-n` - flag indicating that python should search hidden folders and files including files and folders starting with `.`

# Prerequisites
Currently tested manually script on `Windows 10`, and with `Python 3.10.6`.

# Example logged info
```commandline
Collecting metrics for path [c:\users\notarealuser\downloads]
Path [c:\users\notarealuser\downloads] contains [0] folders and [3] items, totaling [0.00TB 0.00GB 3.69MB 708.56KB 572.00B]
Collected metrics in [0.00] seconds
Collecting files in path [c:\users\notarealuser\downloads] which contains [3] files totaling [0.00TB 0.00GB 3.69MB 708.56KB 572.00B]
Processed [2/3] files in [0days 00:00:00] ETA:[0days 00:00:13] based on [0.01%] data processed generating [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] metadata
Collected files in [0days 00:00:00] and built up [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] of metadata
Started searching for duplicates
Found [1] duplicated files having [1] duplicates and totaling [0.00TB 0.00GB 3.69MB 708.28KB 290.00B] in [0days 00:00:00] generating [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] metadata
>>> func:[find_duplicates] took: [0days 00:00:00]
>>> func:[dump_duplicates] took: [0days 00:00:00]
```