# Readme
I have been trying to make some backup system and after a while ended with a lot of duplicate files that end up taking up space.
So I thought about this tool that would help me find out which files are duplicates and ideally remove the duplicates and put some link to the original file thus saving space and allowing for more backups to be stored on a single HDD.

For example processing `15K` files which take up `212GB` HDD takes roughly `40 minutes` to process the hashes, but the overall duplicate identification takes `10 seconds` iterating over a metadata that is less than `100KB` in RAM. 

# Usage
> duplicate-finder.py [path1] [path2] ... -j -l -e -n -c -k [cache_file.cache] -d [log_level]

* `-d` - parameter indicating which log level to use inside script, default:`info`, choices: `critical, error, warning, info, debug, notset`
* `-j` - flag indicating the creation of a dump a file containing a json with list of sequences of duplicates, where the first element in each sequence is the original file found, and all successive ones are duplicates, format `[[original_file, duplicate1, dulicate2, ...], ...]`
* `-l` - flag indicating if backlinks from the duplicates to the original file found should be created
* `-e` - flag indicating that duplicate files should be erased
* `-n` - flag indicating that python should search hidden folders and files including files and folders starting with `.`
* `-c` - flag indicating that script should dump the metadata it generates into a json file with the following structure `[{'path':str, 'size':int, 'time':str, 'checksum':str}, ...]`
* `-k` - parameter indicating the filename of a previously dumped metadata file, it should speed up by skipping rehashing of files already hashed

# Prerequisites
Currently tested manually script on `Windows 10`, and with `Python 3.10.6`.

# Similar projects
* https://github.com/deplicate/deplicate - is a good example of reusable script, and was released as package as well
* https://pypi.org/project/Duplicate-Finder/ - exports a `.csv` file of duplicates
* https://pypi.org/project/duplicate-detector/ - compare 2 folders for similar items, but based on filename alone - can cause loosing of content that is different but with similar filenames
* https://pypi.org/project/find-duplicate-files/ - similar idea - computes partial hash, to speed up things
* https://pypi.org/project/duplicate-image-finder/ - works only with images

# Example runs of script
## Commandline log of first run
```commandline
python duplicate-finder.py c:\users\notarealuser\downloads -j -c

MainThread__2022-09-10_12-37-12.125 Loading cache [2022-08-20_22-31-51_duplicate-finder.cache]
MainThread__2022-09-10_12-37-12.125 Failed to load cache [2022-08-20_22-31-51_duplicate-finder.cache] with exception [[Errno 2] No such file or directory: '2022-08-20_22-31-51_duplicate-finder.cache']
MainThread__2022-09-10_12-37-12.125 Loaded [0] cached files totaling [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-10_12-37-12.125 === func:[load_cache] took: [0days 00:00:00.000]
MainThread__2022-09-10_12-37-12.168 === func:[collect_metrics_in_path] took: [0days 00:00:00.043]
MainThread__2022-09-10_12-37-12.169 Path [c:\users\notarealuser\downloads] contains [10] folders and [556] items, totaling [0.00TB 1.36GB 364.89MB 909.88KB 905.00B]
MainThread__2022-09-10_12-37-15.348 === func:[collect_metrics_in_path] took: [0days 00:00:03.179]
MainThread__2022-09-10_12-37-15.348 Path [D:\__code__] contains [6139] folders and [44709] items, totaling [0.00TB 1.08GB 78.77MB 789.07KB 71.00B]
MainThread__2022-09-10_12-37-15.348 === func:[collect_all_metrics] took: [0days 00:00:03.223]
MainThread__2022-09-10_12-37-15.348 Started processing hashes for files from [2] paths
Thread-5 (thread_print)__2022-09-10_12-37-17.389 Processed [543/556] files in [0days 00:00:02.025] ETA: [0days 00:00:00.674] based on [75.03%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-10_12-37-18.034 Processed [555/556] uncached files in [0days 00:00:02.670] generating [0.00TB 0.00GB 0.00MB 4.68KB 696.00B] metadata
Thread-6 (thread_print)__2022-09-10_12-37-23.186 Processed [7970/44709] files in [0days 00:00:02.001] ETA: [0days 00:00:15.782] based on [11.26%] data processed generating [0.00TB 0.00GB 0.00MB 4.40KB 408.00B] metadata
MainThread__2022-09-10_12-37-31.655 Processed [41797/44709] uncached files in [0days 00:00:10.470] generating [0.00TB 0.00GB 0.33MB 342.84KB 856.00B] metadata
MainThread__2022-09-10_12-37-33.192 === func:[collect_all_files] took: [0days 00:00:17.843]
MainThread__2022-09-10_12-37-33.192 Dumping cache [2022-09-10_12-37-33_duplicate-finder.cache]
MainThread__2022-09-10_12-37-36.991 === func:[dump_cache] took: [0days 00:00:03.798]
MainThread__2022-09-10_12-37-36.991 Started searching for duplicates among [42352] indexed files
Thread-7 (thread_print)__2022-09-10_12-37-39.028 Done [338816/896824776] comparisons of [16/42352] files in [0days 00:00:02.036] ETA: [0days 01:29:49.307] based on [0.04%] comparisons
Thread-7 (thread_print)__2022-09-10_12-38-39.211 Done [40382632/896824776] comparisons of [1907/42352] files in [0days 00:01:02.220] ETA: [0days 00:21:59.575] based on [4.50%] comparisons
Thread-7 (thread_print)__2022-09-10_12-39-39.476 Done [90908568/896824776] comparisons of [4293/42352] files in [0days 00:02:02.484] ETA: [0days 00:18:05.844] based on [10.14%] comparisons
Thread-7 (thread_print)__2022-09-10_12-40-40.440 Done [152509552/896824776] comparisons of [7202/42352] files in [0days 00:03:03.449] ETA: [0days 00:14:55.315] based on [17.01%] comparisons
Thread-7 (thread_print)__2022-09-10_12-41-41.408 Done [218324560/896824776] comparisons of [10310/42352] files in [0days 00:04:04.417] ETA: [0days 00:12:39.589] based on [24.34%] comparisons
Thread-7 (thread_print)__2022-09-10_12-42-41.605 Done [278104408/896824776] comparisons of [13133/42352] files in [0days 00:05:04.614] ETA: [0days 00:11:17.699] based on [31.01%] comparisons
Thread-7 (thread_print)__2022-09-10_12-43-41.816 Done [347286400/896824776] comparisons of [16400/42352] files in [0days 00:06:04.825] ETA: [0days 00:09:37.292] based on [38.72%] comparisons
Thread-7 (thread_print)__2022-09-10_12-44-42.028 Done [424028224/896824776] comparisons of [20024/42352] files in [0days 00:07:05.037] ETA: [0days 00:07:53.921] based on [47.28%] comparisons
Thread-7 (thread_print)__2022-09-10_12-45-42.223 Done [516228528/896824776] comparisons of [24378/42352] files in [0days 00:08:05.231] ETA: [0days 00:05:57.743] based on [57.56%] comparisons
Thread-7 (thread_print)__2022-09-10_12-46-42.420 Done [640912816/896824776] comparisons of [30266/42352] files in [0days 00:09:05.429] ETA: [0days 00:03:37.786] based on [71.46%] comparisons
MainThread__2022-09-10_12-47-31.975 Found [13691] duplicated files having [90150] duplicates and occupying [0.00TB 0.22GB 221.97MB 988.49KB 497.00B] out of [0.00TB 1.71GB 728.61MB 625.57KB 583.00B] in [0days 00:09:54.984] generating [0.00TB 0.00GB 0.12MB 118.59KB 600.00B] metadata
MainThread__2022-09-10_12-47-32.582 === func:[find_duplicates] took: [0days 00:09:55.590]
MainThread__2022-09-10_12-47-32.582 Dumping duplicates file [2022-09-10_12-47-32_duplicate-finder.json]
MainThread__2022-09-10_12-47-46.820 === func:[dump_duplicates] took: [0days 00:00:14.238]
MainThread__2022-09-10_12-47-46.821 Executed script in [0days 00:10:34.700]
```

## Commandline log using cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache
```

## Command line using half cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache
```
