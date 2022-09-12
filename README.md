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
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c
```commandline
MainThread__2022-09-12_13-09-21.131 === func:[collect_metrics_in_path] took: [0days 00:00:00.020]
MainThread__2022-09-12_13-09-21.131 Path [c:\users\mihai\downloads] contains [1] folders and [228] items, totaling [0.00TB 1.31GB 313.11MB 115.71KB 727.00B]
MainThread__2022-09-12_13-09-24.391 === func:[collect_metrics_in_path] took: [0days 00:00:03.259]
MainThread__2022-09-12_13-09-24.391 Path [d:\__code__] contains [6172] folders and [44780] items, totaling [0.00TB 1.15GB 149.25MB 260.69KB 705.00B]
MainThread__2022-09-12_13-09-24.391 === func:[collect_all_metrics] took: [0days 00:00:03.279]
MainThread__2022-09-12_13-09-24.391 Started processing hashes for files from [2] paths
Thread-5 (thread_print)__2022-09-12_13-09-26.431 Processed [67/228] files in [0days 00:00:05.329] ETA: [0days 00:00:29.345] based on [15.37%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-12_13-09-26.880 Processed [228/228] uncached files in [0days 00:00:02.489] generating [0.00TB 0.00GB 0.00MB 1.87KB 888.00B] metadata
MainThread__2022-09-12_13-09-40.303 Processed [45008/44780] uncached files in [0days 00:00:11.867] generating [0.00TB 0.00GB 0.38MB 385.71KB 728.00B] metadata
MainThread__2022-09-12_13-09-41.945 === func:[collect_all_files] took: [0days 00:00:17.553]
MainThread__2022-09-12_13-09-41.945 Dumping cache [2022-09-12_13-09-41_duplicate-finder.cache]
MainThread__2022-09-12_13-09-46.916 === func:[dump_cache] took: [0days 00:00:04.971]
MainThread__2022-09-12_13-09-46.931 Started searching for duplicates among [45008] indexed files
Thread-7 (thread_print)__2022-09-12_13-10-49.142 Compared [17662/45008] files in [0days 00:01:28.041] ETA: [0days 00:02:16.313] based on [39.24%] comparisons
Thread-7 (thread_print)__2022-09-12_13-11-49.324 Compared [23960/45008] files in [0days 00:02:28.223] ETA: [0days 00:02:10.209] based on [53.23%] comparisons
Thread-7 (thread_print)__2022-09-12_13-12-50.091 Compared [29964/45008] files in [0days 00:03:28.989] ETA: [0days 00:01:44.927] based on [66.57%] comparisons
Thread-7 (thread_print)__2022-09-12_13-13-50.460 Compared [33732/45008] files in [0days 00:04:29.359] ETA: [0days 00:01:30.042] based on [74.95%] comparisons
Thread-7 (thread_print)__2022-09-12_13-14-50.884 Compared [37074/45008] files in [0days 00:05:29.783] ETA: [0days 00:01:10.575] based on [82.37%] comparisons
Thread-7 (thread_print)__2022-09-12_13-15-51.077 Compared [39691/45008] files in [0days 00:06:29.976] ETA: [0days 00:00:52.241] based on [88.19%] comparisons
Thread-7 (thread_print)__2022-09-12_13-16-51.301 Compared [42027/45008] files in [0days 00:07:30.200] ETA: [0days 00:00:31.932] based on [93.38%] comparisons
Thread-7 (thread_print)__2022-09-12_13-17-51.685 Compared [44401/45008] files in [0days 00:08:30.584] ETA: [0days 00:00:06.980] based on [98.65%] comparisons
MainThread__2022-09-12_13-18-08.651 Found [7068] duplicated files having [14088] duplicates and occupying [0.00TB 0.05GB 55.15MB 149.43KB 445.00B] out of [0.00TB 2.45GB 462.37MB 376.40KB 408.00B] in [0days 00:08:21.721] generating [0.00TB 0.00GB 0.06MB 58.34KB 344.00B] metadata
MainThread__2022-09-12_13-18-09.808 === func:[find_duplicates] took: [0days 00:08:22.877]
MainThread__2022-09-12_13-18-09.808 Dumping duplicates file [2022-09-12_13-18-09_duplicate-finder.json]
MainThread__2022-09-12_13-18-13.492 === func:[dump_duplicates] took: [0days 00:00:03.684]
MainThread__2022-09-12_13-18-13.492 Executed script in [0days 00:08:52.391]
```
>python duplicate-finder.py c:\users\notarealuser\downloads d:\__code__ -j -c -p
```commandline
MainThread__2022-09-12_13-23-07.100 === func:[collect_metrics_in_path] took: [0days 00:00:00.021]
MainThread__2022-09-12_13-23-07.100 Path [c:\users\mihai\downloads] contains [1] folders and [228] items, totaling [0.00TB 1.31GB 313.11MB 114.56KB 572.00B]
MainThread__2022-09-12_13-23-10.547 === func:[collect_metrics_in_path] took: [0days 00:00:03.447]
MainThread__2022-09-12_13-23-10.547 Path [d:\__code__] contains [6172] folders and [44782] items, totaling [0.00TB 1.16GB 168.71MB 731.08KB 77.00B]
MainThread__2022-09-12_13-23-10.547 === func:[collect_all_metrics] took: [0days 00:00:03.469]
MainThread__2022-09-12_13-23-10.547 Started processing hashes for files from [2] paths
Thread-9 (function)__2022-09-12_13-23-10.674 Thread [3] started processing chunk [87,116] of [228] files with [0] cached files
Thread-6 (function)__2022-09-12_13-23-10.674 Thread [0] started processing chunk [0,29] of [228] files with [0] cached files
Thread-8 (function)__2022-09-12_13-23-10.675 Thread [2] started processing chunk [58,87] of [228] files with [0] cached files
Thread-12 (function)__2022-09-12_13-23-10.675 Thread [6] started processing chunk [174,203] of [228] files with [0] cached files
Thread-11 (function)__2022-09-12_13-23-10.675 Thread [5] started processing chunk [145,174] of [228] files with [0] cached files
Thread-10 (function)__2022-09-12_13-23-10.676 Thread [4] started processing chunk [116,145] of [228] files with [0] cached files
Thread-13 (function)__2022-09-12_13-23-10.676 Thread [7] started processing chunk [203,228] of [228] files with [0] cached files
Thread-7 (function)__2022-09-12_13-23-10.677 Thread [1] started processing chunk [29,58] of [228] files with [0] cached files
Thread-12 (function)__2022-09-12_13-23-10.734 Thread [6] finished processing chunk [174,203] of [228] files with [0] cached files in [0days 00:00:03.662] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-10 (function)__2022-09-12_13-23-10.750 Thread [4] finished processing chunk [116,145] of [228] files with [0] cached files in [0days 00:00:03.678] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-11 (function)__2022-09-12_13-23-10.753 Thread [5] finished processing chunk [145,174] of [228] files with [0] cached files in [0days 00:00:03.681] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-9 (function)__2022-09-12_13-23-10.757 Thread [3] finished processing chunk [87,116] of [228] files with [0] cached files in [0days 00:00:03.684] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-13 (function)__2022-09-12_13-23-10.775 Thread [7] finished processing chunk [203,228] of [228] files with [0] cached files in [0days 00:00:03.704] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-6 (function)__2022-09-12_13-23-10.826 Thread [0] finished processing chunk [0,29] of [228] files with [0] cached files in [0days 00:00:03.755] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-7 (function)__2022-09-12_13-23-10.964 Thread [1] finished processing chunk [29,58] of [228] files with [0] cached files in [0days 00:00:03.892] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
Thread-5 (thread_print)__2022-09-12_13-23-12.676 Processed [208/228] files in [0days 00:00:05.604] ETA: [0days 00:00:19.765] based on [22.09%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
Thread-8 (function)__2022-09-12_13-23-12.815 Thread [2] finished processing chunk [58,87] of [228] files with [0] cached files in [0days 00:00:05.744] generating [0.00TB 0.00GB 0.00MB 0.30KB 312.00B] metadata
MainThread__2022-09-12_13-23-15.560 Processed [228/228] uncached files in [0days 00:00:05.012] generating [0.00TB 0.00GB 0.00MB 1.87KB 888.00B] metadata
Thread-15 (function)__2022-09-12_13-23-16.678 Thread [0] started processing chunk [0,5598] of [44782] files with [228] cached files
Thread-16 (function)__2022-09-12_13-23-16.679 Thread [1] started processing chunk [5598,11196] of [44782] files with [228] cached files
Thread-17 (function)__2022-09-12_13-23-16.681 Thread [2] started processing chunk [11196,16794] of [44782] files with [228] cached files
Thread-18 (function)__2022-09-12_13-23-16.685 Thread [3] started processing chunk [16794,22392] of [44782] files with [228] cached files
Thread-19 (function)__2022-09-12_13-23-16.686 Thread [4] started processing chunk [22392,27990] of [44782] files with [228] cached files
Thread-20 (function)__2022-09-12_13-23-16.688 Thread [5] started processing chunk [27990,33588] of [44782] files with [228] cached files
Thread-21 (function)__2022-09-12_13-23-16.688 Thread [6] started processing chunk [33588,39186] of [44782] files with [228] cached files
Thread-22 (function)__2022-09-12_13-23-16.690 Thread [7] started processing chunk [39186,44782] of [44782] files with [228] cached files
Thread-18 (function)__2022-09-12_13-23-22.494 Thread [3] finished processing chunk [16794,22392] of [44782] files with [228] cached files in [0days 00:00:15.422] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-19 (function)__2022-09-12_13-23-22.664 Thread [4] finished processing chunk [22392,27990] of [44782] files with [228] cached files in [0days 00:00:15.593] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-20 (function)__2022-09-12_13-23-22.707 Thread [5] finished processing chunk [27990,33588] of [44782] files with [228] cached files in [0days 00:00:15.636] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-21 (function)__2022-09-12_13-23-22.715 Thread [6] finished processing chunk [33588,39186] of [44782] files with [228] cached files in [0days 00:00:15.644] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-15 (function)__2022-09-12_13-23-22.717 Thread [0] finished processing chunk [0,5598] of [44782] files with [228] cached files in [0days 00:00:15.645] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-17 (function)__2022-09-12_13-23-22.720 Thread [2] finished processing chunk [11196,16794] of [44782] files with [228] cached files in [0days 00:00:15.649] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-16 (function)__2022-09-12_13-23-22.814 Thread [1] finished processing chunk [5598,11196] of [44782] files with [228] cached files in [0days 00:00:15.743] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
Thread-22 (function)__2022-09-12_13-23-24.029 Thread [7] finished processing chunk [39186,44782] of [44782] files with [228] cached files in [0days 00:00:16.957] generating [0.00TB 0.00GB 0.04MB 46.05KB 56.00B] metadata
MainThread__2022-09-12_13-23-26.692 Processed [45010/44782] uncached files in [0days 00:00:10.015] generating [0.00TB 0.00GB 0.38MB 393.68KB 696.00B] metadata
MainThread__2022-09-12_13-23-30.205 === func:[collect_all_files] took: [0days 00:00:19.657]
MainThread__2022-09-12_13-23-30.205 Dumping cache [2022-09-12_13-23-30_duplicate-finder.cache]
MainThread__2022-09-12_13-23-35.437 === func:[dump_cache] took: [0days 00:00:05.232]
MainThread__2022-09-12_13-23-35.454 Started searching for duplicates among [45010] indexed files
Thread-24 (function)__2022-09-12_13-23-35.456 Thread [0] started processing chunk [8k+0] of [45010] files
Thread-25 (function)__2022-09-12_13-23-35.468 Thread [1] started processing chunk [8k+1] of [45010] files
Thread-26 (function)__2022-09-12_13-23-35.497 Thread [2] started processing chunk [8k+2] of [45010] files
Thread-27 (function)__2022-09-12_13-23-35.501 Thread [3] started processing chunk [8k+3] of [45010] files
Thread-28 (function)__2022-09-12_13-23-35.505 Thread [4] started processing chunk [8k+4] of [45010] files
Thread-29 (function)__2022-09-12_13-23-35.508 Thread [5] started processing chunk [8k+5] of [45010] files
Thread-30 (function)__2022-09-12_13-23-35.515 Thread [6] started processing chunk [8k+6] of [45010] files
Thread-31 (function)__2022-09-12_13-23-35.518 Thread [7] started processing chunk [8k+7] of [45010] files
Thread-23 (thread_print)__2022-09-12_13-24-37.767 Done [1199445900/8101440084] comparisons of [17317/45010] files in [0days 00:01:30.696] ETA: [0days 00:08:41.894] based on [14.81%] comparisons
Thread-23 (thread_print)__2022-09-12_13-25-38.228 Done [2230201580/8101440084] comparisons of [23613/45010] files in [0days 00:02:31.156] ETA: [0days 00:06:37.934] based on [27.53%] comparisons
Thread-23 (thread_print)__2022-09-12_13-26-38.883 Done [3367133288/8101440084] comparisons of [29014/45010] files in [0days 00:03:31.811] ETA: [0days 00:04:57.814] based on [41.56%] comparisons
Thread-23 (thread_print)__2022-09-12_13-27-39.789 Done [4326880216/8101440084] comparisons of [32890/45010] files in [0days 00:04:32.717] ETA: [0days 00:03:57.905] based on [53.41%] comparisons
Thread-23 (thread_print)__2022-09-12_13-28-41.990 Done [5491041588/8101440084] comparisons of [37051/45010] files in [0days 00:05:34.918] ETA: [0days 00:02:39.217] based on [67.78%] comparisons
Thread-23 (thread_print)__2022-09-12_13-29-43.276 Done [6557634776/8101440084] comparisons of [40490/45010] files in [0days 00:06:36.205] ETA: [0days 00:01:33.275] based on [80.94%] comparisons
Thread-23 (thread_print)__2022-09-12_13-30-44.489 Done [7617650784/8101440084] comparisons of [43640/45010] files in [0days 00:07:37.417] ETA: [0days 00:00:29.050] based on [94.03%] comparisons
Thread-26 (function)__2022-09-12_13-31-09.921 Thread [2] finished processing chunk [8k+2] finding [1147] duplicated files with [2653] duplicates in [0days 00:08:02.835] occupying [0.00TB 0.01GB 13.71MB 726.31KB 315.00B]
Thread-30 (function)__2022-09-12_13-31-10.514 Thread [6] finished processing chunk [8k+6] finding [1127] duplicated files with [2408] duplicates in [0days 00:08:03.435] occupying [0.00TB 0.00GB 4.77MB 793.45KB 459.00B]
Thread-29 (function)__2022-09-12_13-31-11.389 Thread [5] finished processing chunk [8k+5] finding [1002] duplicated files with [2115] duplicates in [0days 00:08:04.315] occupying [0.00TB 0.00GB 2.30MB 304.37KB 381.00B]
Thread-25 (function)__2022-09-12_13-31-11.544 Thread [1] finished processing chunk [8k+1] finding [1246] duplicated files with [2808] duplicates in [0days 00:08:04.470] occupying [0.00TB 0.02GB 23.42MB 434.52KB 533.00B]
Thread-28 (function)__2022-09-12_13-31-12.253 Thread [4] finished processing chunk [8k+4] finding [1146] duplicated files with [2463] duplicates in [0days 00:08:05.172] occupying [0.00TB 0.00GB 4.63MB 644.86KB 877.00B]
Thread-31 (function)__2022-09-12_13-31-12.534 Thread [7] finished processing chunk [8k+7] finding [1037] duplicated files with [2120] duplicates in [0days 00:08:05.461] occupying [0.00TB 0.00GB 4.24MB 246.88KB 903.00B]
Thread-24 (function)__2022-09-12_13-31-12.654 Thread [0] finished processing chunk [8k+0] finding [1176] duplicated files with [2792] duplicates in [0days 00:08:05.574] occupying [0.00TB 0.00GB 1.61MB 623.94KB 960.00B]
Thread-27 (function)__2022-09-12_13-31-12.707 Thread [3] finished processing chunk [8k+3] finding [982] duplicated files with [2221] duplicates in [0days 00:08:05.634] occupying [0.00TB 0.00GB 3.39MB 402.58KB 598.00B]
MainThread__2022-09-12_13-31-13.214 Found [8863] duplicated files having [19580] duplicates and occupying [0.00TB 0.06GB 58.08MB 80.91KB 930.00B] out of [0.00TB 2.47GB 481.83MB 845.63KB 649.00B] in [0days 00:07:37.759] generating [0.00TB 0.00GB 0.08MB 77.99KB 1016.00B] metadata
MainThread__2022-09-12_13-31-14.881 === func:[find_duplicates] took: [0days 00:07:39.426]
MainThread__2022-09-12_13-31-14.881 Dumping duplicates file [2022-09-12_13-31-14_duplicate-finder_p.json]
MainThread__2022-09-12_13-31-18.355 === func:[dump_duplicates] took: [0days 00:00:03.474]
MainThread__2022-09-12_13-31-18.356 Executed script in [0days 00:08:11.284]
```