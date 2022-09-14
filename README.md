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

# Time comparison
- Remark: there is a bug in the implementation of the multi-threaded part of the algorithm, so for now its safer to run without `-p` flag.
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c
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
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c -p
```commandline
MainThread__2022-09-14_20-33-47.845 === func:[collect_metrics_in_path] took: [0days 00:00:00.015]
MainThread__2022-09-14_20-33-47.845 Path [c:\users\notarealuser\downloads] contains [2] folders and [249] items, totaling [0.00TB 1.31GB 317.01MB 12.35KB 357.00B]
MainThread__2022-09-14_20-33-59.269 === func:[collect_metrics_in_path] took: [0days 00:00:11.423]
MainThread__2022-09-14_20-33-59.269 Path [d:\__code__] contains [6179] folders and [44827] items, totaling [0.00TB 1.40GB 406.37MB 378.60KB 612.00B]
MainThread__2022-09-14_20-33-59.269 === func:[collect_all_metrics] took: [0days 00:00:11.439]
MainThread__2022-09-14_20-33-59.269 Started processing hashes for files from [2] paths
Thread-13 (function)__2022-09-14_20-33-59.379 Thread [7] started hashing chunk [224,249] of [249] files with [0] cached files
Thread-10 (function)__2022-09-14_20-33-59.379 Thread [4] started hashing chunk [128,160] of [249] files with [0] cached files
Thread-6 (function)__2022-09-14_20-33-59.379 Thread [0] started hashing chunk [0,32] of [249] files with [0] cached files
Thread-7 (function)__2022-09-14_20-33-59.379 Thread [1] started hashing chunk [32,64] of [249] files with [0] cached files
Thread-8 (function)__2022-09-14_20-33-59.379 Thread [2] started hashing chunk [64,96] of [249] files with [0] cached files
Thread-9 (function)__2022-09-14_20-33-59.379 Thread [3] started hashing chunk [96,128] of [249] files with [0] cached files
Thread-11 (function)__2022-09-14_20-33-59.379 Thread [5] started hashing chunk [160,192] of [249] files with [0] cached files
Thread-12 (function)__2022-09-14_20-33-59.379 Thread [6] started hashing chunk [192,224] of [249] files with [0] cached files
Thread-13 (function)__2022-09-14_20-33-59.806 Thread [7] finished hashing chunk [224,249] of [249] files with [0] cached files in [0days 00:00:11.976] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-12 (function)__2022-09-14_20-33-59.806 Thread [6] finished hashing chunk [192,224] of [249] files with [0] cached files in [0days 00:00:11.976] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-10 (function)__2022-09-14_20-33-59.822 Thread [4] finished hashing chunk [128,160] of [249] files with [0] cached files in [0days 00:00:11.992] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-11 (function)__2022-09-14_20-33-59.853 Thread [5] finished hashing chunk [160,192] of [249] files with [0] cached files in [0days 00:00:12.023] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-6 (function)__2022-09-14_20-33-59.853 Thread [0] finished hashing chunk [0,32] of [249] files with [0] cached files in [0days 00:00:12.023] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-9 (function)__2022-09-14_20-33-59.869 Thread [3] finished hashing chunk [96,128] of [249] files with [0] cached files in [0days 00:00:12.039] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-5 (thread_print)__2022-09-14_20-34-01.400 Hashed [213/249] files in [0days 00:00:13.570] ETA: [0days 00:00:59.085] based on [18.68%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Thread-7 (function)__2022-09-14_20-34-02.228 Thread [1] finished hashing chunk [32,64] of [249] files with [0] cached files in [0days 00:00:14.398] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-8 (function)__2022-09-14_20-34-03.712 Thread [2] finished hashing chunk [64,96] of [249] files with [0] cached files in [0days 00:00:15.882] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
MainThread__2022-09-14_20-34-04.279 Hashed [249/249] uncached files in [0days 00:00:05.009] generating [0.00TB 0.00GB 0.00MB 2.05KB 56.00B] metadata
Thread-15 (function)__2022-09-14_20-34-05.431 Thread [0] started hashing chunk [0,5604] of [44827] files with [249] cached files
Thread-16 (function)__2022-09-14_20-34-05.431 Thread [1] started hashing chunk [5604,11208] of [44827] files with [249] cached files
Thread-17 (function)__2022-09-14_20-34-05.431 Thread [2] started hashing chunk [11208,16812] of [44827] files with [249] cached files
Thread-18 (function)__2022-09-14_20-34-05.431 Thread [3] started hashing chunk [16812,22416] of [44827] files with [249] cached files
Thread-19 (function)__2022-09-14_20-34-05.431 Thread [4] started hashing chunk [22416,28020] of [44827] files with [249] cached files
Thread-20 (function)__2022-09-14_20-34-05.431 Thread [5] started hashing chunk [28020,33624] of [44827] files with [249] cached files
Thread-21 (function)__2022-09-14_20-34-05.431 Thread [6] started hashing chunk [33624,39228] of [44827] files with [249] cached files
Thread-22 (function)__2022-09-14_20-34-05.431 Thread [7] started hashing chunk [39228,44827] of [44827] files with [249] cached files
Thread-15 (function)__2022-09-14_20-34-28.319 Thread [0] finished hashing chunk [0,5604] of [44827] files with [249] cached files in [0days 00:00:40.489] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-14 (thread_print)__2022-09-14_20-35-07.693 Hashed [35394/44827] files in [0days 00:01:19.863] ETA: [0days 23:59:35.637] based on [143.89%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Thread-18 (function)__2022-09-14_20-35-22.014 Thread [3] finished hashing chunk [16812,22416] of [44827] files with [249] cached files in [0days 00:01:34.184] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-19 (function)__2022-09-14_20-35-23.162 Thread [4] finished hashing chunk [22416,28020] of [44827] files with [249] cached files in [0days 00:01:35.332] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-17 (function)__2022-09-14_20-35-31.341 Thread [2] finished hashing chunk [11208,16812] of [44827] files with [249] cached files in [0days 00:01:43.511] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-21 (function)__2022-09-14_20-35-31.715 Thread [6] finished hashing chunk [33624,39228] of [44827] files with [249] cached files in [0days 00:01:43.885] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-20 (function)__2022-09-14_20-35-32.634 Thread [5] finished hashing chunk [28020,33624] of [44827] files with [249] cached files in [0days 00:01:44.803] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-16 (function)__2022-09-14_20-35-33.494 Thread [1] finished hashing chunk [5604,11208] of [44827] files with [249] cached files in [0days 00:01:45.664] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-22 (function)__2022-09-14_20-35-41.620 Thread [7] finished hashing chunk [39228,44827] of [44827] files with [249] cached files in [0days 00:01:53.789] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
MainThread__2022-09-14_20-35-45.553 Hashed [45076/44827] uncached files in [0days 00:01:40.122] generating [0.00TB 0.00GB 0.38MB 394.09KB 88.00B] metadata
MainThread__2022-09-14_20-35-47.226 === func:[collect_all_files] took: [0days 00:01:47.956]
MainThread__2022-09-14_20-35-47.226 Dumping cache [2022-09-14_20-35-47_duplicate-finder.cache]
MainThread__2022-09-14_20-35-51.409 === func:[dump_cache] took: [0days 00:00:04.183]
MainThread__2022-09-14_20-35-51.425 Started searching for duplicates among [45076] indexed files
Thread-24 (function)__2022-09-14_20-35-51.452 Thread [0] started processing chunk [8k+0] of [45076] files
Thread-24 (function)__2022-09-14_20-35-51.467 Thread [0] finished comparing chunk [8k+0] finding [197] duplicated files with [560] duplicates in [0days 00:02:03.636] occupying [0.00TB 0.00GB 2.96MB 980.37KB 382.00B]
Thread-25 (function)__2022-09-14_20-35-51.467 Thread [1] started processing chunk [8k+1] of [45076] files
Thread-26 (function)__2022-09-14_20-35-51.477 Thread [2] started processing chunk [8k+2] of [45076] files
Thread-25 (function)__2022-09-14_20-35-51.492 Thread [1] finished comparing chunk [8k+1] finding [176] duplicated files with [476] duplicates in [0days 00:02:03.661] occupying [0.00TB 0.00GB 3.90MB 917.40KB 405.00B]
Thread-27 (function)__2022-09-14_20-35-51.492 Thread [3] started processing chunk [8k+3] of [45076] files
Thread-26 (function)__2022-09-14_20-35-51.505 Thread [2] finished comparing chunk [8k+2] finding [163] duplicated files with [504] duplicates in [0days 00:02:03.675] occupying [0.00TB 0.01GB 13.44MB 453.95KB 977.00B]
Thread-27 (function)__2022-09-14_20-35-51.509 Thread [3] finished comparing chunk [8k+3] finding [183] duplicated files with [441] duplicates in [0days 00:02:03.679] occupying [0.00TB 0.02GB 16.82MB 840.55KB 567.00B]
Thread-28 (function)__2022-09-14_20-35-51.510 Thread [4] started processing chunk [8k+4] of [45076] files
Thread-29 (function)__2022-09-14_20-35-51.522 Thread [5] started processing chunk [8k+5] of [45076] files
Thread-28 (function)__2022-09-14_20-35-51.526 Thread [4] finished comparing chunk [8k+4] finding [191] duplicated files with [644] duplicates in [0days 00:02:03.695] occupying [0.00TB 0.00GB 3.30MB 304.00KB 1021.00B]
Thread-30 (function)__2022-09-14_20-35-51.538 Thread [6] started processing chunk [8k+6] of [45076] files
Thread-29 (function)__2022-09-14_20-35-51.545 Thread [5] finished comparing chunk [8k+5] finding [163] duplicated files with [406] duplicates in [0days 00:02:03.714] occupying [0.00TB 0.00GB 2.95MB 973.70KB 720.00B]
Thread-30 (function)__2022-09-14_20-35-51.554 Thread [6] finished comparing chunk [8k+6] finding [198] duplicated files with [449] duplicates in [0days 00:02:03.722] occupying [0.00TB 0.00GB 2.66MB 676.80KB 819.00B]
Thread-31 (function)__2022-09-14_20-35-51.554 Thread [7] started processing chunk [8k+7] of [45076] files
Thread-31 (function)__2022-09-14_20-35-51.568 Thread [7] finished comparing chunk [8k+7] finding [182] duplicated files with [533] duplicates in [0days 00:02:03.736] occupying [0.00TB 0.00GB 3.28MB 290.06KB 63.00B]
Thread-23 (thread_print)__2022-09-14_20-35-53.425 Done [8123822559/8124498516] comparisons of [45066/45076] files in [0days 00:02:05.595] ETA: [0days 00:00:00.010] based on [99.99%] comparisons
MainThread__2022-09-14_20-35-56.589 Found [1453] duplicated files having [4013] duplicates and occupying [0.00TB 0.05GB 49.31MB 316.84KB 858.00B] out of [0.00TB 2.71GB 723.38MB 390.95KB 969.00B] in [0days 00:00:05.166] generating [0.00TB 0.00GB 0.01MB 12.87KB 888.00B] metadata
MainThread__2022-09-14_20-35-57.428 === func:[find_duplicates] took: [0days 00:00:06.004]
MainThread__2022-09-14_20-35-57.428 Dumping duplicates file [2022-09-14_20-35-57_duplicate-finder_p.json]
MainThread__2022-09-14_20-35-58.175 === func:[dump_duplicates] took: [0days 00:00:00.746]
MainThread__2022-09-14_20-35-58.176 Executed script in [0days 00:02:10.345]
```

# weird
```commandline
MainThread__2022-09-14_20-08-46.371 === func:[collect_metrics_in_path] took: [0days 00:00:00.019]
MainThread__2022-09-14_20-08-46.371 Path [c:\users\notarealuser\downloads] contains [2] folders and [249] items, totaling [0.00TB 1.31GB 317.01MB 12.35KB 357.00B]
MainThread__2022-09-14_20-08-49.632 === func:[collect_metrics_in_path] took: [0days 00:00:03.260]
MainThread__2022-09-14_20-08-49.632 Path [d:\__code__] contains [6174] folders and [44814] items, totaling [0.00TB 1.38GB 393.48MB 496.49KB 499.00B]
MainThread__2022-09-14_20-08-49.632 === func:[collect_all_metrics] took: [0days 00:00:03.280]
MainThread__2022-09-14_20-08-49.632 Started processing hashes for files from [2] paths
Thread-6 (function)__2022-09-14_20-08-49.752 Thread [0] started hashing chunk [0,32] of [249] files with [0] cached files
Thread-12 (function)__2022-09-14_20-08-49.752 Thread [6] started hashing chunk [192,224] of [249] files with [0] cached files
Thread-8 (function)__2022-09-14_20-08-49.752 Thread [2] started hashing chunk [64,96] of [249] files with [0] cached files
Thread-13 (function)__2022-09-14_20-08-49.752 Thread [7] started hashing chunk [224,249] of [249] files with [0] cached files
Thread-11 (function)__2022-09-14_20-08-49.752 Thread [5] started hashing chunk [160,192] of [249] files with [0] cached files
Thread-10 (function)__2022-09-14_20-08-49.752 Thread [4] started hashing chunk [128,160] of [249] files with [0] cached files
Thread-9 (function)__2022-09-14_20-08-49.752 Thread [3] started hashing chunk [96,128] of [249] files with [0] cached files
Thread-7 (function)__2022-09-14_20-08-49.752 Thread [1] started hashing chunk [32,64] of [249] files with [0] cached files
Thread-12 (function)__2022-09-14_20-08-49.812 Thread [6] finished processing chunk [192,224] of [249] files with [0] cached files in [0days 00:00:03.463] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-10 (function)__2022-09-14_20-08-49.822 Thread [4] finished processing chunk [128,160] of [249] files with [0] cached files in [0days 00:00:03.473] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-11 (function)__2022-09-14_20-08-49.832 Thread [5] finished processing chunk [160,192] of [249] files with [0] cached files in [0days 00:00:03.483] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-13 (function)__2022-09-14_20-08-49.842 Thread [7] finished processing chunk [224,249] of [249] files with [0] cached files in [0days 00:00:03.493] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-9 (function)__2022-09-14_20-08-49.852 Thread [3] finished processing chunk [96,128] of [249] files with [0] cached files in [0days 00:00:03.503] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-6 (function)__2022-09-14_20-08-49.892 Thread [0] finished processing chunk [0,32] of [249] files with [0] cached files in [0days 00:00:03.543] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-7 (function)__2022-09-14_20-08-50.083 Thread [1] finished processing chunk [32,64] of [249] files with [0] cached files in [0days 00:00:03.734] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-8 (function)__2022-09-14_20-08-51.707 Thread [2] finished processing chunk [64,96] of [249] files with [0] cached files in [0days 00:00:05.358] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-5 (thread_print)__2022-09-14_20-08-51.762 Processed [249/249] files in [0days 00:00:05.413] ETA: [0days 23:59:59.999] based on [100.00%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-14_20-08-54.652 Processed [249/249] uncached files in [0days 00:00:05.020] generating [0.00TB 0.00GB 0.00MB 2.05KB 56.00B] metadata
Thread-15 (function)__2022-09-14_20-08-55.793 Thread [0] started hashing chunk [0,5602] of [44814] files with [249] cached files
Thread-16 (function)__2022-09-14_20-08-55.793 Thread [1] started hashing chunk [5602,11204] of [44814] files with [249] cached files
Thread-17 (function)__2022-09-14_20-08-55.793 Thread [2] started hashing chunk [11204,16806] of [44814] files with [249] cached files
Thread-18 (function)__2022-09-14_20-08-55.793 Thread [3] started hashing chunk [16806,22408] of [44814] files with [249] cached files
Thread-19 (function)__2022-09-14_20-08-55.793 Thread [4] started hashing chunk [22408,28010] of [44814] files with [249] cached files
Thread-20 (function)__2022-09-14_20-08-55.793 Thread [5] started hashing chunk [28010,33612] of [44814] files with [249] cached files
Thread-21 (function)__2022-09-14_20-08-55.802 Thread [6] started hashing chunk [33612,39214] of [44814] files with [249] cached files
Thread-22 (function)__2022-09-14_20-08-55.802 Thread [7] started hashing chunk [39214,44814] of [44814] files with [249] cached files
Thread-18 (function)__2022-09-14_20-09-02.189 Thread [3] finished processing chunk [16806,22408] of [44814] files with [249] cached files in [0days 00:00:15.840] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-19 (function)__2022-09-14_20-09-02.315 Thread [4] finished processing chunk [22408,28010] of [44814] files with [249] cached files in [0days 00:00:15.966] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-21 (function)__2022-09-14_20-09-02.375 Thread [6] finished processing chunk [33612,39214] of [44814] files with [249] cached files in [0days 00:00:16.026] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-20 (function)__2022-09-14_20-09-02.419 Thread [5] finished processing chunk [28010,33612] of [44814] files with [249] cached files in [0days 00:00:16.070] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-15 (function)__2022-09-14_20-09-02.438 Thread [0] finished processing chunk [0,5602] of [44814] files with [249] cached files in [0days 00:00:16.089] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-17 (function)__2022-09-14_20-09-02.449 Thread [2] finished processing chunk [11204,16806] of [44814] files with [249] cached files in [0days 00:00:16.099] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-16 (function)__2022-09-14_20-09-02.752 Thread [1] finished processing chunk [5602,11204] of [44814] files with [249] cached files in [0days 00:00:16.403] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-22 (function)__2022-09-14_20-09-04.219 Thread [7] finished processing chunk [39214,44814] of [44814] files with [249] cached files in [0days 00:00:17.871] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
MainThread__2022-09-14_20-09-05.812 Processed [45063/44814] uncached files in [0days 00:00:10.019] generating [0.00TB 0.00GB 0.38MB 393.96KB 984.00B] metadata
MainThread__2022-09-14_20-09-07.332 === func:[collect_all_files] took: [0days 00:00:17.699]
MainThread__2022-09-14_20-09-07.332 Dumping cache [2022-09-14_20-09-07_duplicate-finder.cache]
MainThread__2022-09-14_20-09-11.978 === func:[dump_cache] took: [0days 00:00:04.645]
MainThread__2022-09-14_20-09-11.992 Started searching for duplicates among [45063] indexed files
Thread-24 (function)__2022-09-14_20-09-12.022 Thread [0] started processing chunk [8k+0] of [45063] files
Thread-25 (function)__2022-09-14_20-09-12.036 Thread [1] started processing chunk [8k+1] of [45063] files
Thread-25 (function)__2022-09-14_20-09-12.048 Thread [1] finished comparing chunk [8k+1] finding [159] duplicated files with [439] duplicates in [0days 00:00:25.700] occupying [0.00TB 0.00GB 3.54MB 551.33KB 339.00B]
Thread-24 (function)__2022-09-14_20-09-12.052 Thread [0] finished comparing chunk [8k+0] finding [181] duplicated files with [498] duplicates in [0days 00:00:25.703] occupying [0.00TB 0.00GB 2.83MB 853.89KB 911.00B]
Thread-26 (function)__2022-09-14_20-09-12.052 Thread [2] started processing chunk [8k+2] of [45063] files
Thread-26 (function)__2022-09-14_20-09-12.069 Thread [2] finished comparing chunk [8k+2] finding [151] duplicated files with [400] duplicates in [0days 00:00:25.720] occupying [0.00TB 0.00GB 2.45MB 458.97KB 996.00B]
Thread-27 (function)__2022-09-14_20-09-12.069 Thread [3] started processing chunk [8k+3] of [45063] files
Thread-27 (function)__2022-09-14_20-09-12.082 Thread [3] finished comparing chunk [8k+3] finding [160] duplicated files with [362] duplicates in [0days 00:00:25.733] occupying [0.00TB 0.00GB 2.32MB 325.10KB 101.00B]
Thread-28 (function)__2022-09-14_20-09-12.087 Thread [4] started processing chunk [8k+4] of [45063] files
Thread-28 (function)__2022-09-14_20-09-12.102 Thread [4] finished comparing chunk [8k+4] finding [178] duplicated files with [629] duplicates in [0days 00:00:25.753] occupying [0.00TB 0.00GB 3.91MB 935.10KB 102.00B]
Thread-29 (function)__2022-09-14_20-09-12.102 Thread [5] started processing chunk [8k+5] of [45063] files
Thread-29 (function)__2022-09-14_20-09-12.118 Thread [5] finished comparing chunk [8k+5] finding [154] duplicated files with [450] duplicates in [0days 00:00:25.769] occupying [0.00TB 0.01GB 13.67MB 689.81KB 832.00B]
Thread-30 (function)__2022-09-14_20-09-12.120 Thread [6] started processing chunk [8k+6] of [45063] files
Thread-30 (function)__2022-09-14_20-09-12.138 Thread [6] finished comparing chunk [8k+6] finding [185] duplicated files with [414] duplicates in [0days 00:00:25.788] occupying [0.00TB 0.02GB 16.27MB 276.39KB 397.00B]
Thread-31 (function)__2022-09-14_20-09-12.138 Thread [7] started processing chunk [8k+7] of [45063] files
Thread-31 (function)__2022-09-14_20-09-12.152 Thread [7] finished comparing chunk [8k+7] finding [165] duplicated files with [424] duplicates in [0days 00:00:25.803] occupying [0.00TB 0.00GB 3.40MB 410.27KB 272.00B]
MainThread__2022-09-14_20-09-12.169 Found [0] duplicated files having [3616] duplicates and occupying [0.00TB 0.00GB 0.00MB 0.00KB 0.00B] out of [0.00TB 2.69GB 710.50MB 508.84KB 856.00B] in [0days 00:00:00.176] generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-14_20-09-14.012 === func:[find_duplicates] took: [0days 00:00:02.020]
MainThread__2022-09-14_20-09-14.012 Dumping duplicates file [2022-09-14_20-09-14_duplicate-finder_p.json]
MainThread__2022-09-14_20-09-14.013 === func:[dump_duplicates] took: [0days 00:00:00.000]
MainThread__2022-09-14_20-09-14.014 Executed script in [0days 00:00:27.665]
```