# Readme
I have been trying to make some backup system and after a while ended with a lot of duplicate files that end up taking up space.
So I thought about this tool that would help me find out which files are duplicates and ideally remove the duplicates and put some link to the original file thus saving space and allowing for more backups to be stored on a single HDD.

For example processing `15K` files which take up `212GB` HDD takes roughly `40 minutes` to process the hashes, but the overall duplicate identification takes `10 seconds` iterating over a metadata that is less than `100KB` in RAM.

# Algorithm
1. Script will start querying the paths and collect metrics such as number of files and the size of the files.
   - since this takes only a few seconds there is no need to parallelize this yet
2. Script then iterates through the paths and builds up an index `[{'path':str, 'size':int, 'time':str, 'checksum':str}, ...]`.
   - if the `-p` flag is provided then this is done with threads that chunk the total number of files
     - `thread1`: from `0 * len(files) / number_of_threads` to `1 * len(files) / number_of_threads`
     - `thread2`: from `1 * len(files) / number_of_threads` to `2 * len(files) / number_of_threads`
     - `thread3`: from `2 * len(files) / number_of_threads` to `3 * len(files) / number_of_threads`
       - and so on
   - while this is executing a printer thread is running in the background and displaying updates every `60 seconds`
3. Script then sorts the constructed index based on size
5. Script will dump a cache file containing the file index described above if the `-c` flag is provided
4. Script will then iterate the index and compare files building a new index of duplicates `[original_file, duplicate1, dulicate2, ...], ...]`
    - if the `-p` flag is provided then this will be done with threads that iterate the index using the following formula
      - `thread1`: will iterate through files using multiples of `number_of_threads * K + 1`
      - `thread2`: will iterate through files using multiples of `number_of_threads * K + 2`
      - `thread3`: will iterate through files using multiples of `number_of_threads * K + 3`
        - and so on, where `K` is an arbitrary number
      - in order to speed up the chunking process, and because sorting the list of files based on size allows us to see duplicates straight from the sorting
        - this means that files which have same size, have a great chance of being duplicates, while files with different sizes have guaranteed no chance of being duplicates
        - so by processing and finding out which indexes have files that change size we get `changing_indexes` list which is passed to all threads
        - then each thread applies the formula described above for chunking, ensuring no thread overlaps with another thread when doing comparisons
            - this should greatly speed things up, as no `LOCK`s would be needed to ensure consistency of data between threads, as the algorithm itself ensures the consistency
    - while this is executing a printer thread is running in the background and displaying updates every `60 seconds`
5. Script will dump the duplicates if `-j` flag is provided
6. Script will create links from duplicates to duplicated file if `-l` flag is provided
7. Script will remove duplicates if the `-e` flag is provided


# Usage
> duplicate-finder.py [path1] [path2] ... -p -j -l -e -n -c -k [cache_file.cache] -d [log_level] 
* `-p` - flag indicating that parallel threads should be spawned and used to process files for hashes and for comparing the files
* `-j` - flag indicating the creation of a dump a file containing a json with list of sequences of duplicates, where the first element in each sequence is the original file found, and all successive ones are duplicates, format `[[original_file, duplicate1, dulicate2, ...], ...]`
* `-l` - flag indicating if backlinks from the duplicates to the original file found should be created
* `-e` - flag indicating that duplicate files should be erased
* `-n` - flag indicating that python should search hidden folders and files including files and folders starting with `.`
* `-c` - flag indicating that script should dump the metadata it generates into a json file with the following structure `[{'path':str, 'size':int, 'time':str, 'checksum':str}, ...]`
* `-k` - parameter indicating the filename of a previously dumped metadata file, it should speed up by skipping rehashing of files already hashed
* `-d` - parameter indicating which log level to use inside script, default:`info`, choices: `critical, error, warning, info, debug, notset`

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
---
# Time comparison
- Remarks:
  - plus 3 files difference of the logs is from the `.cache` and the `.json` files generated during previous run, which are duplicates of previous runs.
  - expected a bigger time improvement in between the executions however cannot skip comparing files, or double sets of duplicates having same size but different content will be missed

- ```python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c```
```commandline
MainThread__2022-09-14_20-36-40.177 === func:[collect_metrics_in_path] took: [0days 00:00:00.018]
MainThread__2022-09-14_20-36-40.178 Path [c:\users\notarealuser\downloads] contains [2] folders and [249] items, totaling [0.00TB 1.31GB 317.01MB 11.29KB 301.00B]
MainThread__2022-09-14_20-36-43.527 === func:[collect_metrics_in_path] took: [0days 00:00:03.349]
MainThread__2022-09-14_20-36-43.527 Path [d:\__code__] contains [6179] folders and [44829] items, totaling [0.00TB 1.41GB 420.90MB 918.04KB 44.00B]
MainThread__2022-09-14_20-36-43.527 === func:[collect_all_metrics] took: [0days 00:00:03.369]
MainThread__2022-09-14_20-36-43.527 Started processing hashes for files from [2] paths
Thread-5 (thread_print)__2022-09-14_20-36-45.553 Hashed [66/249] files in [0days 00:00:05.397] ETA: [0days 00:00:30.262] based on [15.14%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-14_20-36-46.244 Hashed [249/249] uncached files in [0days 00:00:02.717] generating [0.00TB 0.00GB 0.00MB 2.15KB 152.00B] metadata
MainThread__2022-09-14_20-37-02.281 Hashed [45078/44829] uncached files in [0days 00:00:14.726] generating [0.00TB 0.00GB 0.38MB 385.71KB 728.00B] metadata
MainThread__2022-09-14_20-37-05.097 === func:[collect_all_files] took: [0days 00:00:21.570]
MainThread__2022-09-14_20-37-05.097 Dumping cache [2022-09-14_20-37-05_duplicate-finder.cache]
MainThread__2022-09-14_20-37-09.743 === func:[dump_cache] took: [0days 00:00:04.645]
MainThread__2022-09-14_20-37-09.755 Started searching for duplicates among [45078] indexed files
Thread-7 (thread_print)__2022-09-14_20-38-11.952 Compared [19804/45078] files in [0days 00:01:31.796] ETA: [0days 00:01:57.151] based on [43.93%] comparisons
Thread-7 (thread_print)__2022-09-14_20-39-12.145 Compared [27492/45078] files in [0days 00:02:31.990] ETA: [0days 00:01:37.224] based on [60.99%] comparisons
Thread-7 (thread_print)__2022-09-14_20-40-12.331 Compared [31241/45078] files in [0days 00:03:32.176] ETA: [0days 00:01:33.975] based on [69.30%] comparisons
Thread-7 (thread_print)__2022-09-14_20-41-12.522 Compared [34560/45078] files in [0days 00:04:32.366] ETA: [0days 00:01:22.892] based on [76.67%] comparisons
Thread-7 (thread_print)__2022-09-14_20-42-12.710 Compared [37600/45078] files in [0days 00:05:32.554] ETA: [0days 00:01:06.139] based on [83.41%] comparisons
Thread-7 (thread_print)__2022-09-14_20-43-12.914 Compared [40160/45078] files in [0days 00:06:32.758] ETA: [0days 00:00:48.097] based on [89.09%] comparisons
Thread-7 (thread_print)__2022-09-14_20-44-13.106 Compared [42619/45078] files in [0days 00:07:32.951] ETA: [0days 00:00:26.134] based on [94.55%] comparisons
Thread-7 (thread_print)__2022-09-14_20-45-13.295 Compared [45014/45078] files in [0days 00:08:33.140] ETA: [0days 00:00:00.729] based on [99.86%] comparisons
MainThread__2022-09-14_20-45-15.098 Found [7068] duplicated files having [14088] duplicates and occupying [0.00TB 0.05GB 55.15MB 151.21KB 210.00B] out of [0.00TB 2.72GB 737.91MB 929.34KB 345.00B] in [0days 00:08:05.343] generating [0.00TB 0.00GB 0.06MB 58.34KB 344.00B] metadata
MainThread__2022-09-14_20-45-15.297 === func:[find_duplicates] took: [0days 00:08:05.541]
MainThread__2022-09-14_20-45-15.297 Dumping duplicates file [2022-09-14_20-45-15_duplicate-finder.json]
MainThread__2022-09-14_20-45-18.162 === func:[dump_duplicates] took: [0days 00:00:02.864]
MainThread__2022-09-14_20-45-18.162 Executed script in [0days 00:08:38.007]
```

- ```python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c -p```
```commandline
MainThread__2022-09-14_23-33-49.340 === func:[collect_metrics_in_path] took: [0days 00:00:00.017]
MainThread__2022-09-14_23-33-49.340 Path [c:\users\notarealuser\downloads] contains [2] folders and [249] items, totaling [0.00TB 1.31GB 317.01MB 11.28KB 290.00B]
MainThread__2022-09-14_23-33-52.650 === func:[collect_metrics_in_path] took: [0days 00:00:03.309]
MainThread__2022-09-14_23-33-52.650 Path [d:\__code__] contains [6179] folders and [44905] items, totaling [0.00TB 1.95GB 971.00MB 1.55KB 561.00B]
MainThread__2022-09-14_23-33-52.650 === func:[collect_all_metrics] took: [0days 00:00:03.326]
MainThread__2022-09-14_23-33-52.650 Started processing hashes for files from [2] paths
Thread-11 (function)__2022-09-14_23-33-52.775 Thread [5] started hashing chunk [160,192] of [249] files with [0] cached files
Thread-6 (function)__2022-09-14_23-33-52.775 Thread [0] started hashing chunk [0,32] of [249] files with [0] cached files
Thread-7 (function)__2022-09-14_23-33-52.775 Thread [1] started hashing chunk [32,64] of [249] files with [0] cached files
Thread-13 (function)__2022-09-14_23-33-52.775 Thread [7] started hashing chunk [224,249] of [249] files with [0] cached files
Thread-12 (function)__2022-09-14_23-33-52.775 Thread [6] started hashing chunk [192,224] of [249] files with [0] cached files
Thread-8 (function)__2022-09-14_23-33-52.775 Thread [2] started hashing chunk [64,96] of [249] files with [0] cached files
Thread-9 (function)__2022-09-14_23-33-52.775 Thread [3] started hashing chunk [96,128] of [249] files with [0] cached files
Thread-10 (function)__2022-09-14_23-33-52.775 Thread [4] started hashing chunk [128,160] of [249] files with [0] cached files
Thread-12 (function)__2022-09-14_23-33-52.835 Thread [6] finished hashing chunk [192,224] of [249] files with [0] cached files in [0days 00:00:03.515] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-10 (function)__2022-09-14_23-33-52.845 Thread [4] finished hashing chunk [128,160] of [249] files with [0] cached files in [0days 00:00:03.526] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-11 (function)__2022-09-14_23-33-52.855 Thread [5] finished hashing chunk [160,192] of [249] files with [0] cached files in [0days 00:00:03.535] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-13 (function)__2022-09-14_23-33-52.865 Thread [7] finished hashing chunk [224,249] of [249] files with [0] cached files in [0days 00:00:03.545] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-9 (function)__2022-09-14_23-33-52.880 Thread [3] finished hashing chunk [96,128] of [249] files with [0] cached files in [0days 00:00:03.561] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-6 (function)__2022-09-14_23-33-52.920 Thread [0] finished hashing chunk [0,32] of [249] files with [0] cached files in [0days 00:00:03.600] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-7 (function)__2022-09-14_23-33-53.138 Thread [1] finished hashing chunk [32,64] of [249] files with [0] cached files in [0days 00:00:03.818] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-5 (thread_print)__2022-09-14_23-33-54.845 Hashed [219/249] files in [0days 00:00:05.526] ETA: [0days 00:00:18.407] based on [23.09%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Thread-8 (function)__2022-09-14_23-33-54.876 Thread [2] finished hashing chunk [64,96] of [249] files with [0] cached files in [0days 00:00:05.556] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
MainThread__2022-09-14_23-33-57.675 Hashed [249/249] uncached files in [0days 00:00:05.025] generating [0.00TB 0.00GB 0.00MB 2.05KB 56.00B] metadata
Thread-15 (function)__2022-09-14_23-33-58.866 Thread [0] started hashing chunk [0,5614] of [44905] files with [249] cached files
Thread-16 (function)__2022-09-14_23-33-58.866 Thread [1] started hashing chunk [5614,11228] of [44905] files with [249] cached files
Thread-17 (function)__2022-09-14_23-33-58.875 Thread [2] started hashing chunk [11228,16842] of [44905] files with [249] cached files
Thread-18 (function)__2022-09-14_23-33-58.875 Thread [3] started hashing chunk [16842,22456] of [44905] files with [249] cached files
Thread-19 (function)__2022-09-14_23-33-58.885 Thread [4] started hashing chunk [22456,28070] of [44905] files with [249] cached files
Thread-20 (function)__2022-09-14_23-33-58.885 Thread [5] started hashing chunk [28070,33684] of [44905] files with [249] cached files
Thread-21 (function)__2022-09-14_23-33-58.885 Thread [6] started hashing chunk [33684,39298] of [44905] files with [249] cached files
Thread-22 (function)__2022-09-14_23-33-58.885 Thread [7] started hashing chunk [39298,44905] of [44905] files with [249] cached files
Thread-18 (function)__2022-09-14_23-34-05.329 Thread [3] finished hashing chunk [16842,22456] of [44905] files with [249] cached files in [0days 00:00:16.010] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-19 (function)__2022-09-14_23-34-05.425 Thread [4] finished hashing chunk [22456,28070] of [44905] files with [249] cached files in [0days 00:00:16.105] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-21 (function)__2022-09-14_23-34-05.465 Thread [6] finished hashing chunk [33684,39298] of [44905] files with [249] cached files in [0days 00:00:16.145] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-17 (function)__2022-09-14_23-34-05.515 Thread [2] finished hashing chunk [11228,16842] of [44905] files with [249] cached files in [0days 00:00:16.196] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-20 (function)__2022-09-14_23-34-05.525 Thread [5] finished hashing chunk [28070,33684] of [44905] files with [249] cached files in [0days 00:00:16.205] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-15 (function)__2022-09-14_23-34-05.525 Thread [0] finished hashing chunk [0,5614] of [44905] files with [249] cached files in [0days 00:00:16.205] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-16 (function)__2022-09-14_23-34-06.045 Thread [1] finished hashing chunk [5614,11228] of [44905] files with [249] cached files in [0days 00:00:16.726] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-22 (function)__2022-09-14_23-34-06.965 Thread [7] finished hashing chunk [39298,44905] of [44905] files with [249] cached files in [0days 00:00:17.646] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
MainThread__2022-09-14_23-34-08.901 Hashed [44905/44905] uncached files in [0days 00:00:10.035] generating [0.00TB 0.00GB 0.39MB 394.77KB 792.00B] metadata
MainThread__2022-09-14_23-34-10.335 === func:[collect_all_files] took: [0days 00:00:17.685]
MainThread__2022-09-14_23-34-10.335 Dumping cache [2022-09-14_23-34-10_duplicate-finder.cache]
MainThread__2022-09-14_23-34-14.636 === func:[dump_cache] took: [0days 00:00:04.300]
MainThread__2022-09-14_23-34-14.646 Started searching for duplicates among [45154] indexed files
Thread-24 (function)__2022-09-14_23-34-14.675 Thread [0] started processing chunk [8k+0] of [45154] files
Thread-25 (function)__2022-09-14_23-34-14.715 Thread [1] started processing chunk [8k+1] of [45154] files
Thread-26 (function)__2022-09-14_23-34-14.795 Thread [2] started processing chunk [8k+2] of [45154] files
Thread-27 (function)__2022-09-14_23-34-14.880 Thread [3] started processing chunk [8k+3] of [45154] files
Thread-28 (function)__2022-09-14_23-34-14.950 Thread [4] started processing chunk [8k+4] of [45154] files
Thread-29 (function)__2022-09-14_23-34-15.035 Thread [5] started processing chunk [8k+5] of [45154] files
Thread-30 (function)__2022-09-14_23-34-16.035 Thread [6] started processing chunk [8k+6] of [45154] files
Thread-31 (function)__2022-09-14_23-34-16.475 Thread [7] started processing chunk [8k+7] of [45154] files
Thread-23 (thread_print)__2022-09-14_23-35-20.745 Done [1911948621/8153367636] comparisons of [21853/45154] files in [0days 00:01:31.426] ETA: [0days 00:04:58.453] based on [23.45%] comparisons
Thread-23 (thread_print)__2022-09-14_23-36-23.560 Done [3321453568/8153367636] comparisons of [28812/45154] files in [0days 00:02:34.241] ETA: [0days 00:03:44.384] based on [40.74%] comparisons
Thread-23 (thread_print)__2022-09-14_23-37-24.806 Done [4332788618/8153367636] comparisons of [32909/45154] files in [0days 00:03:35.486] ETA: [0days 00:03:10.012] based on [53.14%] comparisons
Thread-23 (thread_print)__2022-09-14_23-38-25.605 Done [5541362781/8153367636] comparisons of [37219/45154] files in [0days 00:04:36.286] ETA: [0days 00:02:10.231] based on [67.96%] comparisons
Thread-23 (thread_print)__2022-09-14_23-39-26.214 Done [6851051583/8153367636] comparisons of [41383/45154] files in [0days 00:05:36.895] ETA: [0days 00:01:04.040] based on [84.03%] comparisons
Thread-30 (function)__2022-09-14_23-40-16.390 Thread [6] finished comparing chunk [8k+6] finding [954] duplicated files with [1705] duplicates in [0days 00:06:27.005] occupying [0.00TB 0.01GB 6.69MB 702.39KB 403.00B]
Thread-26 (function)__2022-09-14_23-40-25.809 Thread [2] finished comparing chunk [8k+2] finding [904] duplicated files with [1749] duplicates in [0days 00:06:36.469] occupying [0.00TB 0.01GB 10.03MB 35.05KB 52.00B]
Thread-28 (function)__2022-09-14_23-40-26.655 Thread [4] finished comparing chunk [8k+4] finding [937] duplicated files with [2149] duplicates in [0days 00:06:37.323] occupying [0.00TB 0.01GB 6.95MB 973.97KB 997.00B]
Thread-23 (thread_print)__2022-09-14_23-40-27.125 Done [8036037568/8153367636] comparisons of [44821/45154] files in [0days 00:06:37.806] ETA: [0days 00:00:05.808] based on [98.56%] comparisons
Thread-25 (function)__2022-09-14_23-40-28.951 Thread [1] finished comparing chunk [8k+1] finding [834] duplicated files with [1642] duplicates in [0days 00:06:39.623] occupying [0.00TB 0.00GB 3.45MB 456.98KB 1008.00B]
Thread-31 (function)__2022-09-14_23-40-32.761 Thread [7] finished comparing chunk [8k+7] finding [780] duplicated files with [1681] duplicates in [0days 00:06:43.439] occupying [0.00TB 0.01GB 11.69MB 704.34KB 345.00B]
Thread-29 (function)__2022-09-14_23-40-32.794 Thread [5] finished comparing chunk [8k+5] finding [840] duplicated files with [1585] duplicates in [0days 00:06:43.467] occupying [0.00TB 0.01GB 6.03MB 27.96KB 981.00B]
Thread-24 (function)__2022-09-14_23-40-33.721 Thread [0] finished comparing chunk [8k+0] finding [990] duplicated files with [1995] duplicates in [0days 00:06:44.393] occupying [0.00TB 0.02GB 15.74MB 758.81KB 833.00B]
Thread-27 (function)__2022-09-14_23-40-34.168 Thread [3] finished comparing chunk [8k+3] finding [832] duplicated files with [1599] duplicates in [0days 00:06:44.847] occupying [0.00TB 0.00GB 4.31MB 313.93KB 955.00B]
MainThread__2022-09-14_23-40-35.897 Found [7071] duplicated files having [14105] duplicates and occupying [0.00TB 0.06GB 64.88MB 901.44KB 454.00B] out of [0.00TB 3.26GB 264.01MB 12.83KB 851.00B] in [0days 00:06:21.250] generating [0.00TB 0.00GB 0.06MB 62.24KB 248.00B] metadata
MainThread__2022-09-14_23-40-37.172 === func:[find_duplicates] took: [0days 00:06:22.526]
MainThread__2022-09-14_23-40-37.173 Dumping duplicates file [2022-09-14_23-40-37_duplicate-finder_p.json]
MainThread__2022-09-14_23-40-39.719 === func:[dump_duplicates] took: [0days 00:00:02.545]
MainThread__2022-09-14_23-40-39.719 Executed script in [0days 00:06:50.400]
```

## TODO:
1. need to identify HDDs somehow, so that when switching drive letters the cache files can still be valid 
    - this can be done by saving the cached index files on disk

2. need to add a config file which can replace the GLOBAL variables, allowing for better control of script 
    - for example: this is useful for configuring extensions of index files, so that there is no collision with other files used by other tools 
    - take `.cache` files which could conflict with filenames used by some other tools