# Readme
I have been trying to make some backup system and after a while ended with a lot of duplicate files that end up taking up space.
So I thought about this tool that would help me find out which files are duplicates and ideally remove the duplicates and put some link to the original file thus saving space and allowing for more backups to be stored on a single HDD.

For example processing `15K` files which take up `212GB` HDD takes roughly `40 minutes` to process the hashes, but the overall duplicate identification takes `10 seconds` iterating over a metadata that is less than `100KB` in RAM. 

# Usage
> duplicate-finder.py [path1] [path2] ... -j -l -e -n -c -k [cache_file.cache]

* `-j` - flag indicating the creation of a dump a file containing a json with list of sequences of duplicates, where the first element in each sequence is the original file found, and all successive ones are duplicates, format `[[original_file, duplicate1, dulicate2, ...], ...]`
* `-l` - flag indicating if backlinks from the duplicates to the original file found should be created
* `-e` - flag indicating that duplicate files should be erased
* `-n` - flag indicating that python should search hidden folders and files including files and folders starting with `.`
* `-c` - flag indicating that script should dump the metadata it generates into a json file with the following structure `[{'path':str, 'size':int, 'time':str, 'checksum':str}, ...]`
* `-k` - parameter indicating the filename of a previously dumped metadata file, it should speed up by skipping rehashing of files already hashed

# Prerequisites
Currently tested manually script on `Windows 10`, and with `Python 3.10.6`.

# Example runs of script
## Commandline log of first run
```commandline
python duplicate-finder.py c:\users\notarealuser\downloads -j -c

Collecting metrics for path [c:\users\notarealuser\downloads]
Path [c:\users\notarealuser\downloads] contains [0] folders and [3] items, totaling [0.00TB 0.00GB 3.69MB 708.56KB 572.00B]
Collected metrics in [0.00] seconds
Collecting metrics for path [d:\]
Path [d:\] contains [2529] folders and [15280] items, totaling [0.21TB 212.87GB 887.36MB 365.27KB 277.00B]
Collected metrics in [4.93] seconds
Collecting files in path [c:\users\notarealuser\downloads] which contains [3] files totaling [0.00TB 0.00GB 3.69MB 708.56KB 572.00B]
Processed [3/3] files in [0days 00:00:00] ETA:[0days 00:00:00] based on [50.00%] data processed generating [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] metadata
Processed [3/3] uncached files in [0days 00:00:00] generating [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] metadata
Collected files in [0days 00:00:00] and built up [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] of metadata
Collecting files in path [d:\] which contains [15280] files totaling [0.21TB 212.87GB 887.36MB 365.27KB 277.00B]
Processed [17/15280] files in [0days 00:00:00] ETA:[6733days 12:30:27] based on [0.00%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Processed [2019/15280] files in [0days 00:01:06] ETA:[0days 00:45:19] based on [2.38%] data processed generating [0.00TB 0.00GB 0.00MB 2.15KB 152.00B] metadata
Processed [2234/15280] files in [0days 00:02:00] ETA:[0days 00:45:17] based on [4.23%] data processed generating [0.00TB 0.00GB 0.00MB 3.62KB 632.00B] metadata
Processed [2713/15280] files in [0days 00:03:01] ETA:[0days 00:45:03] based on [6.29%] data processed generating [0.00TB 0.00GB 0.01MB 7.65KB 664.00B] metadata
Processed [3066/15280] files in [0days 00:04:00] ETA:[0days 00:40:48] based on [8.95%] data processed generating [0.00TB 0.00GB 0.01MB 8.65KB 664.00B] metadata
Processed [3461/15280] files in [0days 00:05:00] ETA:[0days 00:38:08] based on [11.62%] data processed generating [0.00TB 0.00GB 0.01MB 9.77KB 792.00B] metadata
Processed [3643/15280] files in [0days 00:06:00] ETA:[0days 00:36:48] based on [14.02%] data processed generating [0.00TB 0.00GB 0.01MB 11.02KB 24.00B] metadata
Processed [4460/15280] files in [0days 00:07:00] ETA:[0days 00:35:20] based on [16.56%] data processed generating [0.00TB 0.00GB 0.01MB 12.43KB 440.00B] metadata
Processed [5089/15280] files in [0days 00:08:01] ETA:[0days 00:33:47] based on [19.19%] data processed generating [0.00TB 0.00GB 0.01MB 12.43KB 440.00B] metadata
Processed [5398/15280] files in [0days 00:09:01] ETA:[0days 00:32:21] based on [21.82%] data processed generating [0.00TB 0.00GB 0.01MB 14.02KB 24.00B] metadata
Processed [7003/15280] files in [0days 00:10:00] ETA:[0days 00:30:57] based on [24.42%] data processed generating [0.00TB 0.00GB 0.02MB 20.05KB 56.00B] metadata
Processed [7370/15280] files in [0days 00:11:00] ETA:[0days 00:29:35] based on [27.12%] data processed generating [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] metadata
Processed [7648/15280] files in [0days 00:12:00] ETA:[0days 00:28:19] based on [29.76%] data processed generating [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] metadata
Processed [8113/15280] files in [0days 00:13:04] ETA:[0days 00:27:08] based on [32.50%] data processed generating [0.00TB 0.00GB 0.02MB 25.43KB 440.00B] metadata
Processed [8260/15280] files in [0days 00:14:00] ETA:[0days 00:26:09] based on [34.87%] data processed generating [0.00TB 0.00GB 0.03MB 28.65KB 664.00B] metadata
Processed [8558/15280] files in [0days 00:15:01] ETA:[0days 00:25:01] based on [37.52%] data processed generating [0.00TB 0.00GB 0.03MB 28.65KB 664.00B] metadata
Processed [8977/15280] files in [0days 00:16:01] ETA:[0days 00:23:50] based on [40.19%] data processed generating [0.00TB 0.00GB 0.03MB 28.65KB 664.00B] metadata
Processed [9176/15280] files in [0days 00:17:06] ETA:[0days 00:22:34] based on [43.11%] data processed generating [0.00TB 0.00GB 0.03MB 32.27KB 280.00B] metadata
Processed [9319/15280] files in [0days 00:18:00] ETA:[0days 00:21:34] based on [45.50%] data processed generating [0.00TB 0.00GB 0.03MB 32.27KB 280.00B] metadata
Processed [9479/15280] files in [0days 00:19:02] ETA:[0days 00:20:36] based on [48.02%] data processed generating [0.00TB 0.00GB 0.03MB 32.27KB 280.00B] metadata
Processed [10044/15280] files in [0days 00:20:00] ETA:[0days 00:19:35] based on [50.53%] data processed generating [0.00TB 0.00GB 0.03MB 32.27KB 280.00B] metadata
Processed [10365/15280] files in [0days 00:21:01] ETA:[0days 00:18:26] based on [53.28%] data processed generating [0.00TB 0.00GB 0.04MB 36.34KB 344.00B] metadata
Processed [10848/15280] files in [0days 00:22:03] ETA:[0days 00:17:20] based on [55.99%] data processed generating [0.00TB 0.00GB 0.04MB 36.34KB 344.00B] metadata
Processed [11153/15280] files in [0days 00:23:04] ETA:[0days 00:16:13] based on [58.72%] data processed generating [0.00TB 0.00GB 0.04MB 36.34KB 344.00B] metadata
Processed [11560/15280] files in [0days 00:24:00] ETA:[0days 00:15:10] based on [61.27%] data processed generating [0.00TB 0.00GB 0.04MB 36.34KB 344.00B] metadata
Processed [11791/15280] files in [0days 00:25:08] ETA:[0days 00:14:01] based on [64.18%] data processed generating [0.00TB 0.00GB 0.04MB 40.90KB 920.00B] metadata
Processed [12084/15280] files in [0days 00:26:19] ETA:[0days 00:12:46] based on [67.34%] data processed generating [0.00TB 0.00GB 0.04MB 40.90KB 920.00B] metadata
Processed [12401/15280] files in [0days 00:27:00] ETA:[0days 00:12:03] based on [69.14%] data processed generating [0.00TB 0.00GB 0.04MB 40.90KB 920.00B] metadata
Processed [12879/15280] files in [0days 00:28:00] ETA:[0days 00:11:01] based on [71.76%] data processed generating [0.00TB 0.00GB 0.04MB 40.90KB 920.00B] metadata
Processed [13159/15280] files in [0days 00:29:00] ETA:[0days 00:10:12] based on [73.97%] data processed generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Processed [13247/15280] files in [0days 00:30:00] ETA:[0days 00:09:14] based on [76.46%] data processed generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Processed [13772/15280] files in [0days 00:31:02] ETA:[0days 00:08:09] based on [79.18%] data processed generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Processed [13961/15280] files in [0days 00:32:01] ETA:[0days 00:07:08] based on [81.76%] data processed generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Processed [14014/15280] files in [0days 00:33:00] ETA:[0days 00:06:05] based on [84.44%] data processed generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Processed [14359/15280] files in [0days 00:34:00] ETA:[0days 00:05:03] based on [87.06%] data processed generating [0.00TB 0.00GB 0.05MB 51.84KB 856.00B] metadata
Processed [14825/15280] files in [0days 00:35:00] ETA:[0days 00:04:01] based on [89.69%] data processed generating [0.00TB 0.00GB 0.05MB 51.84KB 856.00B] metadata
Processed [15685/15280] files in [0days 00:36:00] ETA:[0days 00:03:05] based on [92.07%] data processed generating [0.00TB 0.00GB 0.05MB 51.84KB 856.00B] metadata
Processed [16155/15280] files in [0days 00:37:00] ETA:[0days 00:02:08] based on [94.55%] data processed generating [0.00TB 0.00GB 0.06MB 58.34KB 344.00B] metadata
Processed [17083/15280] files in [0days 00:38:01] ETA:[0days 00:01:09] based on [97.04%] data processed generating [0.00TB 0.00GB 0.06MB 65.65KB 664.00B] metadata
Processed [17343/15280] files in [0days 00:39:00] ETA:[0days 00:00:19] based on [99.19%] data processed generating [0.00TB 0.00GB 0.06MB 65.65KB 664.00B] metadata
Processed [17415/15280] uncached files in [0days 00:39:18] generating [0.00TB 0.00GB 0.06MB 65.65KB 664.00B] metadata
Collected files in [0days 00:39:19] and built up [0.00TB 0.00GB 0.06MB 65.65KB 664.00B] of metadata
>>> func:[dump_cache] took: [0days 00:00:00]
Started searching for duplicates
Found [640] duplicated files having [1084] duplicates and occupying [0.01TB 10.50GB 512.79MB 809.63KB 642.00B] out of [0.21TB 212.88GB 900.75MB 771.06KB 65.00B] in [0days 00:00:08] generating [0.00TB 0.00GB 0.01MB 5.30KB 312.00B] metadata
>>> func:[find_duplicates] took: [0days 00:00:13]
>>> func:[dump_duplicates] took: [0days 00:00:00]
```

## Commandline log using cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache

Loaded [7798] cached files totaling [0.00TB 0.00GB 0.06MB 65.65KB 664.00B] metadata
>>> func:[load_cache] took: [0days 00:00:00]
Collecting metrics for path [c:\users\notarealuser\downloads]
Path [c:\users\notarealuser\downloads] contains [0] folders and [1] items, totaling [0.00TB 0.00GB 0.00MB 0.28KB 282.00B]
Collected metrics in [0.00] seconds
Collecting metrics for path [d:\]
Path [d:\] contains [2539] folders and [8088] items, totaling [0.21TB 212.89GB 910.27MB 273.17KB 179.00B]
Collected metrics in [4.46] seconds
Collecting files in path [c:\users\notarealuser\downloads] which contains [1] files totaling [0.00TB 0.00GB 0.00MB 0.28KB 282.00B]
Processed [0/1] uncached files in [0days 00:00:00] generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Collected files in [0days 00:00:00] and built up [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] of metadata
Collecting files in path [d:\] which contains [8088] files totaling [0.21TB 212.89GB 910.27MB 273.17KB 179.00B]
Processed [0/8088] files in [0days 00:00:00] ETA:[2638days 13:28:07] based on [0.00%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Processed [14/8088] uncached files in [0days 00:00:06] generating [0.00TB 0.00GB 0.00MB 0.18KB 184.00B] metadata
Collected files in [0days 00:00:07] and built up [0.00TB 0.00GB 0.00MB 0.18KB 184.00B] of metadata
>>> func:[dump_cache] took: [0days 00:00:00]
Started searching for duplicates
Found [640] duplicated files having [1083] duplicates and occupying [0.01TB 10.50GB 508.54MB 555.95KB 973.00B] out of [0.21TB 212.89GB 910.00MB 1.96KB 981.00B] in [0days 00:00:08] generating [0.00TB 0.00GB 0.01MB 5.30KB 312.00B] metadata
>>> func:[find_duplicates] took: [0days 00:00:08]
>>> func:[dump_duplicates] took: [0days 00:00:00]
```

## Command line using half cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache

Loaded [4991] cached files totaling [0.00TB 0.00GB 0.04MB 40.90KB 920.00B] metadata
>>> func:[load_cache] took: [0days 00:00:00]
Collecting metrics for path [c:\users\notarealuser\downloads]
Path [c:\users\notarealuser\downloads] contains [0] folders and [1] items, totaling [0.00TB 0.00GB 0.00MB 0.28KB 282.00B]
Collected metrics in [0.00] seconds
Collecting metrics for path [d:\]
Path [d:\] contains [2535] folders and [8079] items, totaling [0.21TB 212.89GB 906.94MB 964.99KB 1010.00B]
Collected metrics in [4.64] seconds
Collecting files in path [c:\users\notarealuser\downloads] which contains [1] files totaling [0.00TB 0.00GB 0.00MB 0.28KB 282.00B]
Processed [1/1] uncached files in [0days 00:00:00] generating [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] metadata
Collected files in [0days 00:00:00] and built up [0.00TB 0.00GB 0.00MB 0.09KB 88.00B] of metadata
Collecting files in path [d:\] which contains [8079] files totaling [0.21TB 212.89GB 906.94MB 964.99KB 1010.00B]
Processed [0/8079] files in [0days 00:00:00] ETA:[2639days 03:38:29] based on [0.00%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Processed [239/8079] files in [0days 00:01:00] ETA:[0days 00:46:11] based on [2.13%] data processed generating [0.00TB 0.00GB 0.00MB 2.15KB 152.00B] metadata
Processed [433/8079] files in [0days 00:02:00] ETA:[0days 00:45:56] based on [4.17%] data processed generating [0.00TB 0.00GB 0.00MB 3.62KB 632.00B] metadata
Processed [901/8079] files in [0days 00:03:00] ETA:[0days 00:45:47] based on [6.16%] data processed generating [0.00TB 0.00GB 0.01MB 7.65KB 664.00B] metadata
Processed [988/8079] files in [0days 00:04:03] ETA:[0days 00:41:21] based on [8.95%] data processed generating [0.00TB 0.00GB 0.01MB 8.65KB 664.00B] metadata
Processed [1204/8079] files in [0days 00:05:04] ETA:[0days 00:38:39] based on [11.62%] data processed generating [0.00TB 0.00GB 0.01MB 9.77KB 792.00B] metadata
Processed [1317/8079] files in [0days 00:06:02] ETA:[0days 00:37:12] based on [13.96%] data processed generating [0.00TB 0.00GB 0.01MB 11.02KB 24.00B] metadata
Processed [1406/8079] files in [0days 00:07:01] ETA:[0days 00:35:49] based on [16.39%] data processed generating [0.00TB 0.00GB 0.01MB 12.43KB 440.00B] metadata
Processed [1501/8079] files in [0days 00:08:00] ETA:[0days 00:34:14] based on [18.94%] data processed generating [0.00TB 0.00GB 0.01MB 12.43KB 440.00B] metadata
Processed [1629/8079] files in [0days 00:09:01] ETA:[0days 00:32:47] based on [21.58%] data processed generating [0.00TB 0.00GB 0.01MB 14.02KB 24.00B] metadata
Processed [2477/8079] files in [0days 00:10:03] ETA:[0days 00:31:16] based on [24.32%] data processed generating [0.00TB 0.00GB 0.02MB 20.05KB 56.00B] metadata
Processed [2624/8079] files in [0days 00:11:00] ETA:[0days 00:29:58] based on [26.85%] data processed generating [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] metadata
Processed [2805/8079] files in [0days 00:12:05] ETA:[0days 00:28:33] based on [29.76%] data processed generating [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] metadata
Processed [2818/8079] uncached files in [0days 00:12:10] generating [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] metadata
Collected files in [0days 00:12:11] and built up [0.00TB 0.00GB 0.02MB 22.59KB 600.00B] of metadata
>>> func:[dump_cache] took: [0days 00:00:01]
Started searching for duplicates
Found [639] duplicated files having [1082] duplicates and occupying [0.01TB 10.50GB 507.90MB 919.25KB 255.00B] out of [0.21TB 212.89GB 906.69MB 706.81KB 827.00B] in [0days 00:00:13] generating [0.00TB 0.00GB 0.01MB 5.30KB 312.00B] metadata
>>> func:[find_duplicates] took: [0days 00:00:13]
>>> func:[dump_duplicates] took: [0days 00:00:00]
```