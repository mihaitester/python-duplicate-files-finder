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

# Time comparison
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c
```commandline
MainThread__2022-09-12_11-22-04.338 Loading cache [2022-09-11_11-16-38_duplicate-finder.cache]
MainThread__2022-09-12_11-22-04.338 Failed to load cache [2022-09-11_11-16-38_duplicate-finder.cache] with exception [[Errno 2] No such file or directory: '2022-09-11_11-16-38_duplicate-finder.cache']
MainThread__2022-09-12_11-22-04.338 Loaded [0] cached files totaling [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-12_11-22-04.338 === func:[load_cache] took: [0days 00:00:00.000]
MainThread__2022-09-12_11-22-04.354 === func:[collect_metrics_in_path] took: [0days 00:00:00.015]
MainThread__2022-09-12_11-22-04.354 Path [c:\users\notarealuser\downloads] contains [1] folders and [226] items, totaling [0.00TB 1.31GB 313.10MB 100.27KB 275.00B]
MainThread__2022-09-12_11-22-07.755 === func:[collect_metrics_in_path] took: [0days 00:00:03.401]
MainThread__2022-09-12_11-22-07.755 Path [d:\__code__] contains [6163] folders and [44811] items, totaling [0.00TB 1.12GB 119.30MB 305.37KB 374.00B]
MainThread__2022-09-12_11-22-07.755 === func:[collect_all_metrics] took: [0days 00:00:03.417]
MainThread__2022-09-12_11-22-07.755 Started processing hashes for files from [2] paths
Thread-5 (thread_print)__2022-09-12_11-22-09.803 Processed [65/226] files in [0days 00:00:05.465] ETA: [0days 00:00:30.092] based on [15.37%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-12_11-22-10.287 Processed [226/226] uncached files in [0days 00:00:02.531] generating [0.00TB 0.00GB 0.00MB 1.87KB 888.00B] metadata
MainThread__2022-09-12_11-22-22.606 Processed [45037/44811] uncached files in [0days 00:00:10.787] generating [0.00TB 0.00GB 0.38MB 385.71KB 728.00B] metadata
MainThread__2022-09-12_11-22-25.170 === func:[collect_all_files] took: [0days 00:00:17.414]
MainThread__2022-09-12_11-22-25.170 Dumping cache [2022-09-12_11-22-25_duplicate-finder.cache]
MainThread__2022-09-12_11-22-29.265 === func:[dump_cache] took: [0days 00:00:04.094]
MainThread__2022-09-12_11-22-29.280 Started searching for duplicates among [45037] indexed files
Thread-7 (thread_print)__2022-09-12_11-23-31.734 Compared [12682/45037] files in [0days 00:01:27.396] ETA: [0days 00:03:42.969] based on [28.16%] comparisons
Thread-7 (thread_print)__2022-09-12_11-24-32.147 Compared [17703/45037] files in [0days 00:02:27.808] ETA: [0days 00:03:48.221] based on [39.31%] comparisons
Thread-7 (thread_print)__2022-09-12_11-25-32.721 Compared [21882/45037] files in [0days 00:03:28.382] ETA: [0days 00:03:40.505] based on [48.59%] comparisons
Thread-7 (thread_print)__2022-09-12_11-26-33.496 Compared [25526/45037] files in [0days 00:04:29.157] ETA: [0days 00:03:25.732] based on [56.68%] comparisons
Thread-7 (thread_print)__2022-09-12_11-27-34.144 Compared [28611/45037] files in [0days 00:05:29.806] ETA: [0days 00:03:09.346] based on [63.53%] comparisons
Thread-7 (thread_print)__2022-09-12_11-28-34.654 Compared [31251/45037] files in [0days 00:06:30.315] ETA: [0days 00:02:52.183] based on [69.39%] comparisons
Thread-7 (thread_print)__2022-09-12_11-29-35.450 Compared [33827/45037] files in [0days 00:07:31.112] ETA: [0days 00:02:29.495] based on [75.11%] comparisons
Thread-7 (thread_print)__2022-09-12_11-30-36.150 Compared [36198/45037] files in [0days 00:08:31.812] ETA: [0days 00:02:04.976] based on [80.37%] comparisons
Thread-7 (thread_print)__2022-09-12_11-31-36.944 Compared [38290/45037] files in [0days 00:09:32.606] ETA: [0days 00:01:40.897] based on [85.02%] comparisons
Thread-7 (thread_print)__2022-09-12_11-32-37.852 Compared [40370/45037] files in [0days 00:10:33.513] ETA: [0days 00:01:13.237] based on [89.64%] comparisons
Thread-7 (thread_print)__2022-09-12_11-33-38.628 Compared [42365/45037] files in [0days 00:11:34.290] ETA: [0days 00:00:43.789] based on [94.07%] comparisons
Thread-7 (thread_print)__2022-09-12_11-34-39.026 Compared [44084/45037] files in [0days 00:12:34.688] ETA: [0days 00:00:16.314] based on [97.88%] comparisons
MainThread__2022-09-12_11-35-12.173 Found [21201] duplicated files having [185076] duplicates and occupying [0.00TB 0.45GB 464.12MB 121.49KB 506.00B] out of [0.00TB 2.42GB 432.40MB 405.63KB 649.00B] in [0days 00:12:42.892] generating [0.00TB 0.00GB 0.17MB 168.96KB 984.00B] metadata
MainThread__2022-09-12_11-35-13.212 === func:[find_duplicates] took: [0days 00:12:43.932]
MainThread__2022-09-12_11-35-13.212 Dumping duplicates file [2022-09-12_11-35-13_duplicate-finder.json]
MainThread__2022-09-12_11-35-41.590 === func:[dump_duplicates] took: [0days 00:00:28.377]
MainThread__2022-09-12_11-35-41.590 Executed script in [0days 00:13:37.252]
```
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c -p
```commandline
MainThread__2022-09-12_11-39-13.941 Loading cache [2022-09-11_11-16-38_duplicate-finder.cache]
MainThread__2022-09-12_11-39-13.941 Failed to load cache [2022-09-11_11-16-38_duplicate-finder.cache] with exception [[Errno 2] No such file or directory: '2022-09-11_11-16-38_duplicate-finder.cache']
MainThread__2022-09-12_11-39-13.941 Loaded [0] cached files totaling [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-12_11-39-13.941 === func:[load_cache] took: [0days 00:00:00.000]
MainThread__2022-09-12_11-39-13.956 === func:[collect_metrics_in_path] took: [0days 00:00:00.014]
MainThread__2022-09-12_11-39-13.956 Path [c:\users\notarealuser\downloads] contains [1] folders and [227] items, totaling [0.00TB 1.31GB 313.10MB 104.84KB 863.00B]
MainThread__2022-09-12_11-39-16.322 === func:[collect_metrics_in_path] took: [0days 00:00:02.365]
MainThread__2022-09-12_11-39-16.322 Path [d:\__code__] contains [6167] folders and [44819] items, totaling [0.00TB 1.19GB 197.74MB 758.14KB 146.00B]
MainThread__2022-09-12_11-39-16.322 === func:[collect_all_metrics] took: [0days 00:00:02.380]
MainThread__2022-09-12_11-39-16.322 Started processing hashes for files from [2] paths
Thread-2 (function)__2022-09-12_11-39-16.324 Thread [0] started processing chunk [0,29] of [227] files with [0] cached files
Thread-3 (function)__2022-09-12_11-39-16.324 Thread [1] started processing chunk [29,58] of [227] files with [0] cached files
Thread-4 (function)__2022-09-12_11-39-16.325 Thread [2] started processing chunk [58,87] of [227] files with [0] cached files
Thread-5 (function)__2022-09-12_11-39-16.325 Thread [3] started processing chunk [87,116] of [227] files with [0] cached files
Thread-6 (function)__2022-09-12_11-39-16.325 Thread [4] started processing chunk [116,145] of [227] files with [0] cached files
Thread-7 (function)__2022-09-12_11-39-16.326 Thread [5] started processing chunk [145,174] of [227] files with [0] cached files
Thread-8 (function)__2022-09-12_11-39-16.326 Thread [6] started processing chunk [174,203] of [227] files with [0] cached files
Thread-9 (function)__2022-09-12_11-39-16.326 Thread [7] started processing chunk [203,227] of [227] files with [0] cached files
Thread-8 (function)__2022-09-12_11-39-16.376 Thread [6] finished processing chunk [174,203] of [227] files with [0] cached files in [0days 00:00:02.441] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-6 (function)__2022-09-12_11-39-16.377 Thread [4] finished processing chunk [116,145] of [227] files with [0] cached files in [0days 00:00:02.442] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-7 (function)__2022-09-12_11-39-16.391 Thread [5] finished processing chunk [145,174] of [227] files with [0] cached files in [0days 00:00:02.456] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-5 (function)__2022-09-12_11-39-16.395 Thread [3] finished processing chunk [87,116] of [227] files with [0] cached files in [0days 00:00:02.460] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-9 (function)__2022-09-12_11-39-16.408 Thread [7] finished processing chunk [203,227] of [227] files with [0] cached files in [0days 00:00:02.473] generating [0.00TB 0.00GB 0.00MB 0.24KB 248.00B] metadata
Thread-2 (function)__2022-09-12_11-39-16.454 Thread [0] finished processing chunk [0,29] of [227] files with [0] cached files in [0days 00:00:02.519] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-3 (function)__2022-09-12_11-39-16.586 Thread [1] finished processing chunk [29,58] of [227] files with [0] cached files in [0days 00:00:02.652] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-1 (thread_print)__2022-09-12_11-39-18.324 Processed [223/227] files in [0days 00:00:04.390] ETA: [0days 00:00:00.029] based on [99.33%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Thread-4 (function)__2022-09-12_11-39-18.342 Thread [2] finished processing chunk [58,87] of [227] files with [0] cached files in [0days 00:00:04.408] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
MainThread__2022-09-12_11-39-21.326 Processed [227/227] uncached files in [0days 00:00:05.003] generating [0.00TB 0.00GB 0.00MB 1.87KB 888.00B] metadata
Thread-11 (function)__2022-09-12_11-39-22.327 Thread [0] started processing chunk [0,5603] of [44819] files with [227] cached files
Thread-12 (function)__2022-09-12_11-39-22.328 Thread [1] started processing chunk [5603,11206] of [44819] files with [227] cached files
Thread-13 (function)__2022-09-12_11-39-22.330 Thread [2] started processing chunk [11206,16809] of [44819] files with [227] cached files
Thread-14 (function)__2022-09-12_11-39-22.331 Thread [3] started processing chunk [16809,22412] of [44819] files with [227] cached files
Thread-15 (function)__2022-09-12_11-39-22.335 Thread [4] started processing chunk [22412,28015] of [44819] files with [227] cached files
Thread-16 (function)__2022-09-12_11-39-22.337 Thread [5] started processing chunk [28015,33618] of [44819] files with [227] cached files
Thread-17 (function)__2022-09-12_11-39-22.340 Thread [6] started processing chunk [33618,39221] of [44819] files with [227] cached files
Thread-18 (function)__2022-09-12_11-39-22.341 Thread [7] started processing chunk [39221,44819] of [44819] files with [227] cached files
Thread-14 (function)__2022-09-12_11-39-26.823 Thread [3] finished processing chunk [16809,22412] of [44819] files with [227] cached files in [0days 00:00:12.888] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-15 (function)__2022-09-12_11-39-26.917 Thread [4] finished processing chunk [22412,28015] of [44819] files with [227] cached files in [0days 00:00:12.983] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-13 (function)__2022-09-12_11-39-26.946 Thread [2] finished processing chunk [11206,16809] of [44819] files with [227] cached files in [0days 00:00:13.012] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-17 (function)__2022-09-12_11-39-26.946 Thread [6] finished processing chunk [33618,39221] of [44819] files with [227] cached files in [0days 00:00:13.012] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-16 (function)__2022-09-12_11-39-26.951 Thread [5] finished processing chunk [28015,33618] of [44819] files with [227] cached files in [0days 00:00:13.017] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-11 (function)__2022-09-12_11-39-26.974 Thread [0] finished processing chunk [0,5603] of [44819] files with [227] cached files in [0days 00:00:13.040] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-12 (function)__2022-09-12_11-39-27.096 Thread [1] finished processing chunk [5603,11206] of [44819] files with [227] cached files in [0days 00:00:13.161] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-18 (function)__2022-09-12_11-39-28.169 Thread [7] finished processing chunk [39221,44819] of [44819] files with [227] cached files in [0days 00:00:14.234] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
MainThread__2022-09-12_11-39-32.344 Processed [45046/44819] uncached files in [0days 00:00:10.017] generating [0.00TB 0.00GB 0.38MB 393.99KB 1016.00B] metadata
MainThread__2022-09-12_11-39-34.532 === func:[collect_all_files] took: [0days 00:00:18.210]
MainThread__2022-09-12_11-39-34.532 Dumping cache [2022-09-12_11-39-34_duplicate-finder.cache]
MainThread__2022-09-12_11-39-34.812 === func:[dump_cache] took: [0days 00:00:00.279]
MainThread__2022-09-12_11-39-34.819 Started searching for duplicates among [45046] indexed files
Thread-20 (function)__2022-09-12_11-39-34.819 Thread [0] started processing chunk [8k+0] of [45046] files
Thread-21 (function)__2022-09-12_11-39-34.831 Thread [1] started processing chunk [8k+1] of [45046] files
Thread-22 (function)__2022-09-12_11-39-34.909 Thread [2] started processing chunk [8k+2] of [45046] files
Thread-23 (function)__2022-09-12_11-39-34.926 Thread [3] started processing chunk [8k+3] of [45046] files
Thread-24 (function)__2022-09-12_11-39-35.020 Thread [4] started processing chunk [8k+4] of [45046] files
Thread-25 (function)__2022-09-12_11-39-35.079 Thread [5] started processing chunk [8k+5] of [45046] files
Thread-26 (function)__2022-09-12_11-39-35.146 Thread [6] started processing chunk [8k+6] of [45046] files
Thread-27 (function)__2022-09-12_11-39-35.263 Thread [7] started processing chunk [8k+7] of [45046] files
Thread-19 (thread_print)__2022-09-12_11-40-36.996 Done [4939702440/8112965204] comparisons of [35142/45046] files in [0days 00:01:23.062] ETA: [0days 00:00:53.359] based on [60.89%] comparisons
Thread-22 (function)__2022-09-12_11-41-28.202 Thread [2] finished processing chunk [8k+2] finding [1244] duplicated files with [3190] duplicates in [0days 00:02:14.267] occupying [0.00TB 0.01GB 10.15MB 154.20KB 209.00B]
Thread-23 (function)__2022-09-12_11-41-28.209 Thread [3] finished processing chunk [8k+3] finding [1258] duplicated files with [3145] duplicates in [0days 00:02:14.274] occupying [0.00TB 0.01GB 15.34MB 348.33KB 340.00B]
Thread-26 (function)__2022-09-12_11-41-28.241 Thread [6] finished processing chunk [8k+6] finding [1077] duplicated files with [2927] duplicates in [0days 00:02:14.306] occupying [0.00TB 0.01GB 5.55MB 563.28KB 289.00B]
Thread-24 (function)__2022-09-12_11-41-28.257 Thread [4] finished processing chunk [8k+4] finding [1318] duplicated files with [3135] duplicates in [0days 00:02:14.321] occupying [0.00TB 0.03GB 30.74MB 753.49KB 499.00B]
Thread-25 (function)__2022-09-12_11-41-28.264 Thread [5] finished processing chunk [8k+5] finding [1150] duplicated files with [2967] duplicates in [0days 00:02:14.329] occupying [0.00TB 0.03GB 33.73MB 749.05KB 50.00B]
Thread-20 (function)__2022-09-12_11-41-28.271 Thread [0] finished processing chunk [8k+0] finding [1584] duplicated files with [4335] duplicates in [0days 00:02:14.335] occupying [0.00TB 0.01GB 10.31MB 315.42KB 430.00B]
Thread-21 (function)__2022-09-12_11-41-28.272 Thread [1] finished processing chunk [8k+1] finding [1297] duplicated files with [3121] duplicates in [0days 00:02:14.337] occupying [0.00TB 0.01GB 6.29MB 296.75KB 773.00B]
Thread-27 (function)__2022-09-12_11-41-28.273 Thread [7] finished processing chunk [8k+7] finding [1031] duplicated files with [2823] duplicates in [0days 00:02:14.338] occupying [0.00TB 0.01GB 7.41MB 415.83KB 846.00B]
MainThread__2022-09-12_11-41-30.451 Found [9959] duplicated files having [25643] duplicates and occupying [0.00TB 0.12GB 119.51MB 524.36KB 364.00B] out of [0.00TB 2.50GB 510.84MB 862.99KB 1009.00B] in [0days 00:01:55.632] generating [0.00TB 0.00GB 0.08MB 78.55KB 568.00B] metadata
MainThread__2022-09-12_11-41-31.121 === func:[find_duplicates] took: [0days 00:01:56.301]
MainThread__2022-09-12_11-41-31.121 Dumping duplicates file [2022-09-12_11-41-31_duplicate-finder.json_p]
MainThread__2022-09-12_11-41-33.365 === func:[dump_duplicates] took: [0days 00:00:02.244]
MainThread__2022-09-12_11-41-33.366 Executed script in [0days 00:02:19.431]
```