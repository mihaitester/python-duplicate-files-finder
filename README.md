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

MainThread__2022-09-10_11-49-22.427 Loading cache [2022-08-20_22-31-51_duplicate-finder.cache]
MainThread__2022-09-10_11-49-22.427 Failed to load cache [2022-08-20_22-31-51_duplicate-finder.cache] with exception [[Errno 2] No such file or directory: '2022-08-20_22-31-51_duplicate-finder.cache']
MainThread__2022-09-10_11-49-22.427 Loaded [0] cached files totaling [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-10_11-49-22.427 === func:[load_cache] took: [0days 00:00:00.000]
MainThread__2022-09-10_11-49-22.474 === func:[collect_metrics_in_path] took: [0days 00:00:00.046]
MainThread__2022-09-10_11-49-22.474 Path [c:\users\notarealuser\downloads] contains [10] folders and [556] items, totaling [0.00TB 1.36GB 364.89MB 909.88KB 905.00B]
MainThread__2022-09-10_11-49-25.896 === func:[collect_metrics_in_path] took: [0days 00:00:03.422]
MainThread__2022-09-10_11-49-25.896 Path [D:\__code__] contains [6134] folders and [44753] items, totaling [0.00TB 1.77GB 788.88MB 898.69KB 707.00B]
MainThread__2022-09-10_11-49-25.896 === func:[collect_all_metrics] took: [0days 00:00:03.469]
MainThread__2022-09-10_11-49-25.896 Started processing hashes for files from [2] paths
Thread-5 (thread_print)__2022-09-10_11-49-27.944 Processed [543/556] files in [0days 00:00:02.032] ETA: [0days 00:00:00.676] based on [75.03%] data processed generating [0.00TB 0.00GB 0.00MB 0.05KB 56.00B] metadata
MainThread__2022-09-10_11-49-28.539 Processed [555/556] uncached files in [0days 00:00:02.626] generating [0.00TB 0.00GB 0.00MB 4.68KB 696.00B] metadata
Thread-6 (thread_print)__2022-09-10_11-49-33.616 Processed [6266/44753] files in [0days 00:00:02.015] ETA: [0days 00:00:06.985] based on [22.39%] data processed generating [0.00TB 0.00GB 0.00MB 4.40KB 408.00B] metadata
MainThread__2022-09-10_11-49-42.866 Processed [41848/44753] uncached files in [0days 00:00:11.264] generating [0.00TB 0.00GB 0.33MB 342.84KB 856.00B] metadata
MainThread__2022-09-10_11-49-43.671 === func:[collect_all_files] took: [0days 00:00:17.775]
MainThread__2022-09-10_11-49-43.671 Dumping cache [2022-09-10_11-49-43_duplicate-finder.cache]
MainThread__2022-09-10_11-49-47.406 === func:[dump_cache] took: [0days 00:00:03.734]
MainThread__2022-09-10_11-49-47.406 Started searching for duplicates among [42403] indexed files
Thread-7 (thread_print)__2022-09-10_11-49-49.452 Done [318022/898986003] comparisons of [15/42403] files in [0days 00:00:02.046] ETA: [0days 01:36:22.766] based on [0.04%] comparisons
Thread-7 (thread_print)__2022-09-10_11-50-50.393 Done [50756391/898986003] comparisons of [2394/42403] files in [0days 00:01:02.986] ETA: [0days 00:17:32.623] based on [5.65%] comparisons
Thread-7 (thread_print)__2022-09-10_11-51-51.198 Done [111986323/898986003] comparisons of [5282/42403] files in [0days 00:02:03.792] ETA: [0days 00:14:29.968] based on [12.46%] comparisons
Thread-7 (thread_print)__2022-09-10_11-52-51.947 Done [178707443/898986003] comparisons of [8429/42403] files in [0days 00:03:04.540] ETA: [0days 00:12:23.790] based on [19.88%] comparisons
Thread-7 (thread_print)__2022-09-10_11-53-52.814 Done [252806686/898986003] comparisons of [11924/42403] files in [0days 00:04:05.407] ETA: [0days 00:10:27.267] based on [28.12%] comparisons
Thread-7 (thread_print)__2022-09-10_11-54-53.772 Done [338948380/898986003] comparisons of [15987/42403] files in [0days 00:05:06.366] ETA: [0days 00:08:26.203] based on [37.70%] comparisons
Thread-7 (thread_print)__2022-09-10_11-55-54.744 Done [443810999/898986003] comparisons of [20933/42403] files in [0days 00:06:07.337] ETA: [0days 00:06:16.743] based on [49.37%] comparisons
Thread-7 (thread_print)__2022-09-10_11-56-55.476 Done [574539448/898986003] comparisons of [27099/42403] files in [0days 00:07:08.070] ETA: [0days 00:04:01.734] based on [63.91%] comparisons
Thread-7 (thread_print)__2022-09-10_11-57-56.231 Done [887409984/898986003] comparisons of [41856/42403] files in [0days 00:08:08.824] ETA: [0days 00:00:06.376] based on [98.71%] comparisons
MainThread__2022-09-10_11-57-56.356 Found [13697] duplicated files having [90156] duplicates and occupying [0.00TB 0.35GB 354.97MB 996.16KB 167.00B] out of [0.00TB 2.41GB 414.73MB 749.24KB 244.00B] in [0days 00:08:08.949] generating [0.00TB 0.00GB 0.12MB 118.59KB 600.00B] metadata
MainThread__2022-09-10_11-57-58.250 === func:[find_duplicates] took: [0days 00:08:10.843]
MainThread__2022-09-10_11-57-58.250 Dumping duplicates file [2022-09-10_11-57-58_duplicate-finder.json]
MainThread__2022-09-10_11-58-10.716 === func:[dump_duplicates] took: [0days 00:00:12.466]
```

## Commandline log using cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache
```

## Command line using half cached files
```commandline
c:\users\notarealuser\downloads d:\ -j -c -k 2022-08-20_21-24-22_duplicate-finder.cache
```
