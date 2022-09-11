import argparse
import copy
import glob
import os
import hashlib
import datetime
import json
import pathlib
import subprocess
import sys
import time
import logging

import time
import sys
import threading
import multiprocessing


DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
ENCODING = "ISO-8859-1"  # help: [ https://www.codegrepper.com/code-examples/python/UnicodeDecodeError%3A+%27utf-16-le%27+codec+can%27t+decode+bytes+in+position+60-61%3A+illegal+UTF-16+surrogate ]

# help: [ https://docs.python.org/3/howto/logging.html#logging-advanced-tutorial ]
# help: [ https://docs.python.org/3/library/time.html#time.strftime ]
# help: [ https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format ]
LOG_FORMATTER = logging.Formatter(fmt='%(threadName)s__%(asctime)s.%(msecs)03d %(message)s', datefmt=DATETIME_FORMAT)
LOGGER = logging.Logger(__file__)


# todo: add a way to configure what base units to use, like days, or weeks, TB or PB, which are used in logging


def timeit(f):
    """
    help: [ https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator ]
    :param f:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        LOGGER.debug('>>> func:[{}] started @ [{}]'.format(f.__name__, ts))
        result = f(*args, **kw)
        te = time.time()
        LOGGER.debug('<<< func:[{}] ended @ [{}]'.format(f.__name__, te))
        LOGGER.info('=== func:[{}] took: [{}]'.format(f.__name__, print_time(te - ts)))
        return result
    return timed


# help: [ https://stackoverflow.com/questions/8600161/executing-periodic-actions ] - every timeout print out current progress
# help: [ https://superfastpython.com/thread-share-variables/ ] - how to share data with the printing thread
# help: [ https://docs.python.org/3/library/threading.html ] - basics of python threading
# help: [ https://stackoverflow.com/questions/3221655/python-threading-string-arguments ] - pass arguments to thread




# todo: collect size of the metadata generated from each thread and properly display all the metadata generated
def print_collecting_ETA(start_time, timeout):
    global PRINT_POPUP_COUNT, PRINT_ETA
    global THREAD_FILES_PROCESSED_COUNT, THREAD_FILES_PROCESSED_SIZE
    global METRIC
    if (time.time() - start_time) / timeout > PRINT_POPUP_COUNT:
        PRINT_POPUP_COUNT += 1
        PRINT_ETA = (METRIC["size"] - THREAD_FILES_PROCESSED_SIZE) * (time.time() - start_time) / THREAD_FILES_PROCESSED_SIZE
        LOGGER.info("Processed [{}/{}] files in [{}] ETA: [{}] based on [{:.2f}%] data processed generating [{}] metadata".format(
                THREAD_FILES_PROCESSED_COUNT,
                METRIC["files"],
                print_time(time.time() - start_time),
                print_time(PRINT_ETA),
                THREAD_FILES_PROCESSED_SIZE / METRIC["size"] * 100,
                print_size(sys.getsizeof(FILES))
            ))


def print_duplicates_ETA(start_time, timeout):
    # todo: change how the ETA is calculated, use an average mean of the chunks processed so far by each thread - currently, depeding on thread different estimates displayed
    global PRINT_POPUP_COUNT, PRINT_ETA
    global THREAD_PROGRESS
    global FILES
    if (time.time() - start_time) / timeout > PRINT_POPUP_COUNT:
        PRINT_POPUP_COUNT += 1
        # print("Compared [{}/{}] files in [{}] ETA: [{}]".format(i+1, len(files), print_time(time.time()-m_start_time), print_time( ( len(files)-i ) * (time.time() - m_start_time) / len(files) )))
        done_comparisons = []
        total_comparisons = []
        lower_limit = []
        upper_limit = []
        chunk = len(FILES) / THREAD_COUNT
        for i in range(THREAD_COUNT):
            # lower_limit.append(chunk * i)
            # upper_limit.append(chunk * (i+1))
            # done_comparisons.append( int((p_progress[i] - lower_limit[i]) * (p_progress[i] - lower_limit[i] - 1) / 2) )
            # total_comparisons.append( int((upper_limit[i] - lower_limit[i]) * (upper_limit[i] - lower_limit[i] - 1) / 2) )
            lower_limit.append(i)
            upper_limit.append(len(FILES) - (len(FILES) % THREAD_COUNT) )
            done_comparisons.append(int((THREAD_PROGRESS[i] - lower_limit[i]) * (THREAD_PROGRESS[i] - lower_limit[i] - 1) / 2))
            total_comparisons.append(int((upper_limit[i] - lower_limit[i]) * (upper_limit[i] - lower_limit[i] - 1) / 2))
        PRINT_ETA = (sum(total_comparisons) - sum(done_comparisons)) * (time.time() - start_time) / sum(done_comparisons)
        LOGGER.info(
            "Done [{}/{}] comparisons of [{}/{}] files in [{}] ETA: [{}] based on [{:.2f}%] comparisons".format(
                sum(done_comparisons),
                sum(total_comparisons),
                int((sum(THREAD_PROGRESS) - sum(lower_limit)) / THREAD_COUNT),
                len(FILES),
                print_time(time.time() - start_time),
                print_time(PRINT_ETA),
                # todo: fix this approximation, need to use comparisons as base number instead of files
                sum(done_comparisons) / sum(total_comparisons) * 100))


# note: because there is a single printing thread there is no need for the `threading.Lock()`, also `thread_print` function is always started from `MainThread`
PRINT_FINISHED = False
PRINT_POPUP_COUNT = 0
PRINT_ETA = 2
def thread_print(function=print_collecting_ETA, start_time=time.time(), timeout=60, micro=2):
    # help: [ https://stackoverflow.com/questions/8600161/executing-periodic-actions ] - every timeout print out current progress
    # help: [ https://superfastpython.com/thread-share-variables/ ] - how to share data with the printing thread
    # help: [ https://docs.python.org/3/library/threading.html ] - basics of python threading
    # help: [ https://stackoverflow.com/questions/3221655/python-threading-string-arguments ] - pass arguments to thread
    # help: [ https://www.geeksforgeeks.org/passing-function-as-an-argument-in-python/ ] - sending print function as parameter
    time.sleep(micro) # note: delay the start of the printing thread such that some data gets processed and better estimates are shown
    while True:
        function(start_time, timeout)
        # note: instead of waiting the full timeout use micro sleeps and check if mainthread finished in the meantime
        for i in range(int(timeout/micro)):
            if PRINT_FINISHED:
                return
            time.sleep(micro)


# todo: replace global variables with some shared memory object containing required data
# need these to be global
# todo: optimize this based on battery levels as well or power policy - because running full throttle the CPU does not guarantee optimal speed and energy consumption
THREAD_FINISHED = []
THREAD_S = []
THREAD_COUNT = multiprocessing.cpu_count()
THREAD_LOCK = threading.Lock() # help: [ https://www.pythontutorial.net/python-concurrency/python-threading-lock/ ] - needed to protect `THREAD_FINISHED` from getting corrupted

THREAD_FILES_PROCESSED_COUNT = 0
THREAD_FILES_PROCESSED_SIZE = 1 # note: avoid division by 0
THREAD_FILES_CACHED_SKIPPED = 0
THREAD_PROGRESS = []
THREAD_FILES_PROCESSED = []
THREAD_FILES_DUPLICATES = 0

# need to have this global
METRIC = {}
FILES = []

# need to have this global
all_duplicates = {}
class ThreadWithResult(threading.Thread):
    # help: [ https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python ] - this shows that `.result` will contain return value after `.join()`
    # help: [ https://superfastpython.com/thread-return-values/ ] - for some reason getting NoneType
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon) # todo: fix this overload as it renames the thread function


def thread_process_duplicates(index, items, start_time=time.time(), timeout=60, micro=2):
    # note: this parallelization increased the execution time from `11min` to `16min` on folder of 2GB containing `.git` and `node_modules`, so chunking bellow a specific number of files actually introduces more overhead instead of speeding up processing
    # note: instead of chunking, better to use 8k+1,8k+2...,8k+7 splitting of FILES
    global THREAD_FINISHED, THREAD_S, THREAD_COUNT, THREAD_LOCK
    global THREAD_PROGRESS, THREAD_FILES_PROCESSED, THREAD_FILES_DUPLICATES
    global FILES # note: this is very important, update the global variables so that threads see the actual data

    # duplicates = {}
    duplicates = []
    duplicates_indexes = []
    # duplicated_paths = []

    # chunk = int(len(FILES) / p_thread_count) + 1  # add 1 file overlap so that all files get processed
    # lower_limit = chunk * index
    # upper_limit = chunk * (index + 1) # - 1 # note: remove the overlapping sections
    # if upper_limit > len(FILES):
    #     upper_limit = len(FILES)

    # LOGGER.info("Thread [{}] started processing chunk [{},{}] of [{}] files".format(index, chunk * index, upper_limit, len(items)))

    # all_duplicates = []

    # todo: BUG: duplicates will be reinserted in the list of duplicates, need to check if a file was already found as duplicated, then it should not be added to the list again
    # for i in range(len(items) - 1):
    i = index
    # note: because the files are sorted on size, need to figure out how to trim the list if duplicates are found

    end = len(FILES)
    while i < end:
    # for i in range(lower_limit, upper_limit):
        with THREAD_LOCK:
            # print_duplicates_ETA()
            THREAD_PROGRESS[index] = i

        # if "duplicated" not in FILES[i].keys():
        if not THREAD_FILES_PROCESSED[i]:
        # if FILES[i] != None:
            # todo: optimize search, by comparing only files that have the same size, which would run faster
            # if items[i] not in all_duplicates:
            duplicates_for_file = []
            duplicates_for_file.append(FILES[i])
            # duplicates_for_file = [FILES[i]]  # [comment1]: consider the 0 index of each list as the original file
            # duplicates_for_file = []  # [comment1]: consider the 0 index of each list as the original file
            # todo: because this is incremental select search, first threads have a bigger chunk to process than subsequent threads, hence need to either change this search, or redistribute workload to finishing threads - dynamic loading for thread pooling
            if FILES[i]["size"] != 0:
                for j in range(len(FILES)): # note: going through all the elements will create a list of duplicates for each file
                # for j in range(i+1, len(items)):  # note: [comment3] if already marked duplicates its pointless to backcheck files that were processed already
                #     if "duplicated" not in FILES[j].keys():
                #     if FILES[j] != None:
                    if not THREAD_FILES_PROCESSED[j]:
                        # print("{} - {}".format(i,j))
                        if i != j: # important: because of using multi-threading the first thread to inject a line of duplicates wins
                            if FILES[i]["size"] < FILES[j]["size"]:  # note: [comment3] thanks to presorting of items, can skip comparisons that eat time, in this case sorted list increasing
                            # if items[i]["size"] < items[j]["size"] or items[i]["size"] > items[j]["size"]: # note: [comment3] thanks to presorting of items, can skip comparisons that eat time
                                break
                            if FILES[i]["size"] > FILES[j]["size"]:  # note: [comment3] thanks to presorting of items, can skip comparisons that eat time, in this case sorted list increasing
                            # if items[i]["size"] < items[j]["size"] or items[i]["size"] > items[j]["size"]: # note: [comment3] thanks to presorting of items, can skip comparisons that eat time
                                continue
                            if FILES[i]["size"] == FILES[j]["size"]:
                                if FILES[i]["checksum"] == FILES[j]["checksum"]:
                                    LOGGER.debug("Found duplicate [{}] for file [{}]".format(FILES[j]["path"], FILES[i]["path"]))
                                    duplicates_for_file.append(FILES[j])
                                    duplicates_indexes.append(j) # note: this should improve performance a lot if after each file that gets processed we de-index its duplicates so the search space is smaller
            else:
                # if items[i]["size"] == 0:
                # todo: figure out what to do with  having size 0, because they can pollute disks as well
                LOGGER.debug("Found empty file [{}]".format(FILES[i]["path"]))
                # todo: figure out if same name files in different folders

            if len(duplicates_for_file) > 1:
            # if len(duplicates_for_file) > 0:
                LOGGER.debug("Found total [{}] duplicates for file [{}]".format(len(duplicates_for_file)-1, FILES[i]["path"]))
                # duplicates_for_file.sort(key=lambda y: y["time"])  # sort duplicate files, preserving oldest one, improve for [comment1]

                # consistency check, because it seems files could have been doubly inserted in the list of files
                # for k in range(len(duplicates_for_file) - 1, 0, -1):
                #     if duplicates_for_file[k]["path"] == items[i]["path"]:
                #         duplicates_for_file.pop(k)
                # if len(duplicates_for_file) > 0:

                duplicates.append(duplicates_for_file)
                duplicates_indexes.sort(reverse=True)

                with THREAD_LOCK:
                    for k in range(len(duplicates_indexes)):
                        # FILES.pop(duplicates_indexes[k])
                        # FILES[duplicates_indexes[k]]["duplicated"] = FILES[i]
                        # FILES[duplicates_indexes[k]] = None
                        THREAD_FILES_PROCESSED[duplicates_indexes[k]] = True
                    THREAD_FILES_PROCESSED[i] = True
                        # duplicates.update({items[i]["path"]:duplicates_for_file}) # observation: execution time drastically increased when working with `dict` instead of `list`, apparently each `dict.update` slows down dramatically the script, time increased from `40min` to over `2hours`
                        # all_duplicates.append(duplicates_for_file)  # based on [comment1], only if a list of duplicates contains more than 1 element, then there are duplicates
                        # obj = {items[i]:duplicates_for_file}
                        # duplicates.update(obj)  # based on [comment1], only if a list of duplicates contains more than 1 element, then there are duplicates
                # with p_lock:
                    THREAD_FILES_DUPLICATES += len(duplicates_for_file) - 1 # based on [comment1], first item in a sequence of duplicates is an original
                    end = len(FILES)

        i += THREAD_COUNT

    with THREAD_LOCK:
        THREAD_FINISHED[index] = True

    # LOGGER.info("Thread [{}] finished processing chunk [{},{}] finding [{}] duplicated files with [{}] duplicates in [{}] occupying [{}]".format(index, lower_limit, upper_limit, len(all_duplicates), sum([len(x) - 1 for x in all_duplicates]), print_time(time.time() - m_start_time), print_size(sum([sum([x[i]["size"] for i in range(1, len(x))]) for x in all_duplicates]) if len(all_duplicates) > 0 else 0)))
    # LOGGER.info("Thread [{}] finished processing chunk [{},{}] finding [{}] duplicated files with [{}] duplicates in [{}] occupying [{}]".format(index, lower_limit, upper_limit, len(all_duplicates.keys()), sum([len(x) - 1 for x in all_duplicates.keys()]), print_time(time.time() - m_start_time), print_size(sum([sum([x[i]["size"] for i in range(1, len(x))]) for x in all_duplicates.keys()]) if len(all_duplicates.keys()) > 0 else 0)))

    return duplicates


def thread_process_hashes(index, cached_files, cached_paths, start_time=time.time(), timeout=60, micro=2):
    # note: added threading and overall result increased from `10min` to `11min` - interesting result, perhaps threading of hashing works better on large files, whereas serial execution is optimal on small files
    # todo: randomize the list of items such that all threads get to process large and small files, or have a redistribution algorithm in place when a thread finishes, if precomputing the list of files to include size and have it sorted in decreasing order
    global THREAD_FINISHED, THREAD_S, THREAD_COUNT, THREAD_LOCK
    global THREAD_FILES_PROCESSED_COUNT, THREAD_FILES_PROCESSED_SIZE, THREAD_FILES_CACHED_SKIPPED

    chunk = int( len(METRIC["items"]) / THREAD_COUNT ) + 1 # add 1 file overlap so that all files get processed
    lower_limit = chunk * index
    upper_limit = chunk * (index + 1)
    if upper_limit > len(METRIC["items"]):
        upper_limit = len(METRIC["items"])

    LOGGER.info("Thread [{}] started processing chunk [{},{}] of [{}] files with [{}] cached files".format(index, chunk * index, upper_limit, len(METRIC["items"]), len(cached_files)))

    items = []

    if len(cached_files) > 0:
        for file in METRIC['items'][lower_limit:upper_limit]:
            # # todo: this is the problem, need to construct the file list when collecting metrics, and then convert that list into chunks that get individually processed
            # for fileref in filter: # note: using the fileref has some advantages, as the processing is way faster
            # print_collecting_ETA()
            # file = str(fileref)
            if os.path.isfile(file):
                THREAD_FILES_PROCESSED_COUNT += 1
                # print(file)
                # todo: use multi-threading to speed up processing of files, split main list into [number of threads] chunks
                # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
                # todo: maybe optimize cache this way and do binary search using file size - for huge lists of files above 100K it could optimize the search speeds
                # todo: one idea to optimize the total run time is to compute the hashes only for files that have same size, but computing hashes of files could be useful for identifying changed files in the future, thus ensuring different versions of same file are also backed up
                # if file not in [x["path"] for x in cached_files]:  # todo: figure out if this optimizes or delays script, hoping else branch triggers if cached not provided
                if file not in cached_paths:  # todo: figure out if this optimizes or delays script, hoping else branch triggers if cached not provided
                    LOGGER.debug("Found uncached file [{}]".format(file))
                    item = {'path': file,
                            'size': os.path.getsize(file),
                            'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
                            'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING)
                            }
                    THREAD_FILES_PROCESSED_SIZE += item['size']
                    items.append(item)
                else:
                    LOGGER.debug("Skipped already indexed file [{}]".format(file))
                    THREAD_FILES_CACHED_SKIPPED += 1  # this means file is already indexed so we skip rehashing it
                    pass
    else:
        for file in METRIC['items'][lower_limit:upper_limit]:
            # # todo: this is the problem, need to construct the file list when collecting metrics, and then convert that list into chunks that get individually processed
            # for fileref in filter: # note: using the fileref has some advantages, as the processing is way faster
            # print_collecting_ETA()
            # file = str(fileref)
            if os.path.isfile(file):
                THREAD_FILES_PROCESSED_COUNT += 1
                # print(file)
                # todo: use multi-threading to speed up processing of files, split main list into [number of threads] chunks
                # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
                # todo: maybe optimize cache this way and do binary search using file size - for huge lists of files above 100K it could optimize the search speeds
                # todo: one idea to optimize the total run time is to compute the hashes only for files that have same size, but computing hashes of files could be useful for identifying changed files in the future, thus ensuring different versions of same file are also backed up
                LOGGER.debug("Caching file [{}]".format(file))
                item = {'path': file,
                        'size': os.path.getsize(file),
                        'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
                        'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING)
                        # todo: figure out elevation for files that are in system folders does not work even if console is admin
                        }
                THREAD_FILES_PROCESSED_SIZE += item['size']
                items.append(item)

    LOGGER.info(
        "Thread [{}] finished processing chunk [{},{}] of [{}] files with [{}] cached files in [{}] generating [{}] metadata".format(
            index, lower_limit, upper_limit, len(METRIC["items"]), len(cached_files),
            print_time(time.time() - start_time), print_size(sys.getsizeof(items))))

    with THREAD_LOCK:
        THREAD_FINISHED[index] = True # signal thread finished, mainthread will collect its results and clear the thread

    return items


@timeit
def dump_cache(items=[]):
    """
    :param items:
    :return:
    """
    cache_file = "{}_{}".format(datetime.datetime.now().strftime(DATETIME_FORMAT),
                                ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".cache")
    try:
        LOGGER.info("Dumping cache [{}]".format(cache_file))
        with open(cache_file, "w", encoding=ENCODING) as dumpfile:
            dumpfile.write(json.dumps(items, indent=4))
        LOGGER.debug("Dumped cache [{}]".format(cache_file))
    except Exception as ex:
        LOGGER.error("Failed to dump cache [{}] with exception [{}]".format(cache_file), ex.message)


@timeit
def load_cache(cache_file=""):
    # todo: integrate this with collecting files, if the file is already indexed then its pointless to compute its cache - this could optimize a lot if there are huge files, for which computing the hash takes longer
    #  for a lot of small files its potentially better to no use cache, and have script recompute hashes than double check hash is not computed already
    # global files
    items = []
    cached_paths = []
    try:
        LOGGER.info("Loading cache [{}]".format(cache_file))
        with open(cache_file, "r", encoding=ENCODING) as readfile:
            items = json.loads(readfile.read())
        LOGGER.debug("Loaded cache [{}]".format(cache_file))
    except Exception as ex:
        LOGGER.error("Failed to load cache [{}] with exception [{}]".format(cache_file, str(ex)))

    # validate that cached files can be found on disk, if not strip the cache of files not found
    LOGGER.debug("Stripping files from cache")
    loaded_files = len(items)
    for i in range(len(items)-1, 0, -1):
        if not os.path.exists(items[i]["path"]):
                items.pop(i)
    LOGGER.debug("Stripped [{}] files from cache that are not on disk".format(loaded_files - len(items)))
    items.sort(key=lambda x: x["size"])
    items.reverse()
    cached_paths = [x["path"] for x in items]
    LOGGER.info("Loaded [{}] cached files totaling [{}] metadata".format(len(items), print_size(sys.getsizeof(items))))
    return items, cached_paths


@timeit
def dump_duplicates(items=[]):
    """
    help: [ https://appdividend.com/2022/06/02/how-to-convert-python-list-to-json/ ] - dumping objects to json
    # :param items: [[original_file, duplicate1, duplicate2, ...], ...]
    :param items: {original_file: [duplicate1, duplicate2, ...], ...}
    :return:
    """
    duplicates_file = "{}_{}".format(datetime.datetime.now().strftime(DATETIME_FORMAT),
                                    ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".json")
    try:
        LOGGER.info("Dumping duplicates file [{}]".format(duplicates_file))
        with open(duplicates_file, "w", encoding=ENCODING) as dumpfile:
            dumpfile.write(json.dumps(items, indent=4))
        LOGGER.debug("Dumped duplicates file [{}]".format(duplicates_file))
    except Exception as ex:
        LOGGER.error("Failed to dump duplicates file [{}] with exception [{}]".format(duplicates_file, ex.message))


@timeit
def link_back_duplicates(items=[]):
    """
    help: [ https://stackoverflow.com/questions/1447575/symlinks-on-windows ]
    help: [ https://pypi.org/project/pywin32/ ]
    :param items: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in items:
        for i in range(1, len(series)):
            try:
                LOGGER.info("Linking [{}] to file [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"]))
                os.link('{}'.format(series[0]["path"]), '{}.lnk'.format(series[i]["path"]))
                LOGGER.debug("Linked [{}] to file [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"]))
                # subprocess.call(['mklink', '"{}.lnk"'.format(series[i]["path"]), '"{}"'.format(series[0]["path"])], shell=True) # note: does not have sufficient priviledges
            except Exception as ex:
                LOGGER.error("Failed linking [{}] to file [{}] with exception [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"], ex.message))


@timeit
def delete_duplicates(items=[]):
    """
    :param items: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in items:
        for i in range(1, len(series)):
            try:
                LOGGER.info("Deleting [{}]".format(series[i]["path"]))
                os.remove(series[i]["path"])
                LOGGER.debug("Deleted [{}]".format(series[i]["path"]))
            except Exception as ex:
                LOGGER.error("Failed to delete [{}] with exception [{}]".format(series[i]["path"], ex.message))


@timeit
def find_duplicates(items=[], parallelize=True):
    """
    :param items: [{path:str,size:int,checksum:str}, ...]
    :return: [[original_file, duplicate1, duplicate2, ...], ...]
    """
    start_time = time.time()

    # note: start the printing thread, could put it in a wrapper, but nesting wrappers adds performance overhead
    global PRINT_FINISHED
    PRINT_FINISHED = False
    print_thread = threading.Thread(target=thread_print, args=[print_duplicates_ETA])
    print_thread.daemon = True
    print_thread.start()

    global THREAD_FINISHED, THREAD_S, THREAD_PROGRESS, THREAD_COUNT, THREAD_LOCK
    global THREAD_FILES_PROCESSED
    global FILES

    LOGGER.info("Started searching for duplicates among [{}] indexed files".format( len(items)) )

    # all_duplicates = {}
    all_duplicates = []
    # m_duplicates = 0
    # m_processed = 0
    # m_popouts = 0

    # important: without this presorting, cannot use the optimization of skipping comparisons in `thread_process_duplicates`
    items.sort(key=lambda x: x["size"])  # sort the files based on size, easier to do comparisons

    if parallelize:
        # help: [ https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python ]
        # todo: thread throttleing, need to figure out solution to throttleing and optimize the number of threads
        # todo: thread dynamic loading, if a thread finishes processing, have another thread chunk its data again, and spread the load
        with THREAD_LOCK:
            THREAD_FINISHED = [False] * THREAD_COUNT
            THREAD_S = [None] * THREAD_COUNT
            THREAD_PROGRESS = [0] * THREAD_COUNT
            THREAD_FILES_PROCESSED = [False] * len(FILES)

        for i in range(THREAD_COUNT):
            # todo: figure out if chunking is possible, as passing items to each thread creates duplicated lists which occupy-RAM and slow down processor, despite being used as read-only resource
            p = ThreadWithResult(target=thread_process_duplicates, args=[i, items])
            p.daemon = True
            with THREAD_LOCK: # need to protect shared list so it propagates value in all threads
                THREAD_S[i] = p
            p.start()

        # note: while not finished processing, sleep for a while and then check again if threads finished
        # todo: adapt the sleep timeout based on ETA reported by each thread, that way remove aggressive pooling which adds overhead
        while False in THREAD_FINISHED:
            # timeout = int(ETA / 2)
            # if timeout > m_pop_timeout:
            #     timeout = m_pop_timeout
            # if timeout < 2:
            #     timeout = 2
            # # print("Sleeping ... [{}]".format( timeout ))
            # time.sleep( timeout )
            # todo: ideally track status of threads across time, would help a lot to print changes in this array when they happen
            # LOGGER.debug("Finished threads: [{}]".format(p_finished))
            time.sleep(5)
            for i in range(THREAD_COUNT):
                if THREAD_S[i] and THREAD_FINISHED[i]:
                    LOGGER.debug("Finished threads: [{}]".format(THREAD_FINISHED))
                    with THREAD_LOCK:
                        THREAD_S[i].join()
                        # all_duplicates.update(p_threads[i].result) # todo: figure out if chunking algorithm works for this because its wrongfully identifying `92K` duplicates for `45K` total files
                        all_duplicates += THREAD_S[i].result # todo: figure out if chunking algorithm works for this because its wrongfully identifying `92K` duplicates for `45K` total files
                        THREAD_S[i] = None
    else:
        pass
        # for i in range(len(items) - 1):
        #     # print_duplicates_ETA()
        #     # todo: optimize search, by comparing only files that have the same size, which would run faster
        #     duplicates_for_file = [items[i]]  # [comment1]: consider the 0 index of each list as the original file
        #     for j in range(i + 1, len(items)):
        #         # print("{} - {}".format(i,j))
        #         if items[i]["size"] == items[j]["size"] and items[i]["checksum"] == items[j]["checksum"] and items[i]["size"] != 0:
        #             LOGGER.debug("Found duplicate [{}] for file [{}]".format(items[j]["path"], items[i]["path"]))
        #             duplicates_for_file.append(items[j])
        #         else:
        #             if items[i]["size"] == 0:
        #                 # todo: figure out what to do with  having size 0, because they can pollute disks as well
        #                 LOGGER.debug("Found empty file [{}]".format(items[i]["path"]))
        #     if len(duplicates_for_file) > 1:
        #         LOGGER.debug("Found total [{}] duplicates for file [{}]".format(len(duplicates_for_file)-1, items[i]["path"]))
        #         duplicates_for_file.sort(key=lambda y: y["time"])  # sort duplicate files, preserving oldest one, improve for [comment1]
        #         all_duplicates.append(duplicates_for_file)  # based on [comment1], only if a list of duplicates contains more than 1 element, then there are duplicates
        #         m_duplicates += len(duplicates_for_file) - 1 # based on [comment1], first item in a sequence of duplicates is an original

    LOGGER.info("Found [{}] duplicated files having [{}] duplicates and occupying [{}] out of [{}] in [{}] generating [{}] metadata".format(
        len(all_duplicates),
        m_duplicates,
        print_size(sum([sum([x[i]["size"] for i in range(1, len(x))]) for x in all_duplicates]) if len(all_duplicates) > 0 else 0),
        print_size(sum([x["size"] for x in items])),
        print_time(time.time() - start_time),
        print_size(sys.getsizeof(all_duplicates))))

    # note: stop the printing thread
    PRINT_FINISHED = True
    print_thread.join()

    return all_duplicates


def collect_files_in_path(path="", hidden=False, metric={}, cached_files=[], cached_paths=[], parallelize=True):
    """
    help: [ https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times ] - use the proper time flag
    help: [ https://stackoverflow.com/questions/49047402/python-3-6-glob-include-hidden-files-and-folders ] - glob no longer includes all files
    :param path:
    :param hidden: flag indicating if searching through hidden files
    :param files: list of files that have been pre-cached, should improve performance
    :return:
    """
    start_time = time.time()

    # note: start the printing thread, could put it in a wrapper, but nesting wrappers adds performance overhead
    global PRINT_FINISHED
    PRINT_FINISHED = False
    print_thread = threading.Thread(target=thread_print, args=[print_collecting_ETA])
    print_thread.daemon = True
    print_thread.start()

    global THREAD_FINISHED, THREAD_S, THREAD_PROGRESS, THREAD_COUNT, THREAD_LOCK
    global m_popouts, m_files, m_size, m_cached, m_finished # note: this is very important, update global variables so that printing threads see actual data

    items = []
    # filter = pathlib.Path(path).glob('**/*')  # get hidden files
    # if hidden != True:
    #     filter = glob.glob(os.path.join(path, "**/*"), recursive=True) + \
    #              glob.glob(os.path.join(path, ".**/*"), recursive=True)  # get recursively inside folders

    m_popouts = 0
    m_files = 0
    m_size = 1 # avoid division by 0
    m_cached = 0

    if parallelize:
        # help: [ https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python ]
        # todo: thread throttleing, need to figure out solution to throttleing and optimize the number of threads
        # todo: thread dynamic loading, if a thread finishes processing, have another thread chunk its data again, and spread the load
        with THREAD_LOCK:
            THREAD_FINISHED = [False] * THREAD_COUNT
            THREAD_S = [None] * THREAD_COUNT

        for i in range(THREAD_COUNT):
            p = ThreadWithResult(target=thread_process_hashes, args=[i, cached_files, cached_paths])  # pass the timeout on start of thread
            p.daemon = True
            with THREAD_LOCK:
                THREAD_S[i] = p
            p.start()

        # note: while not finished processing, sleep for a while and then check again if threads finished
        # todo: adapt the sleep timeout based on ETA reported by each thread, that way remove aggressive pooling which adds overhead
        while False in THREAD_FINISHED:
            # timeout = int(ETA / 2)
            # if timeout > m_pop_timeout:
            #     timeout = m_pop_timeout
            # if timeout < 2:
            #     timeout = 2
            # # print("Sleeping ... [{}]".format( timeout ))
            # time.sleep( timeout )
            # todo: ideally track status of threads across time, would help a lot to print changes in this array when they happen
            # LOGGER.debug("Finished threads: [{}]".format(p_finished))
            time.sleep(5)
            for i in range(THREAD_COUNT):
                if THREAD_S[i] and THREAD_FINISHED[i]:
                    LOGGER.debug("Finished threads: [{}]".format(THREAD_FINISHED))
                    with THREAD_LOCK:
                        THREAD_S[i].join()
                        items += THREAD_S[i].result
                        THREAD_S[i] = None
    else:
        pass
    # # important: [comment2] using a list of paths, instead of filter increased the processing time from `10min` to `16min`
    # for file in METRIC['items']:
    # # # todo: this is the problem, need to construct the file list when collecting metrics, and then convert that list into chunks that get individually processed
    # # for fileref in filter: # note: using the fileref has some advantages, as the processing is way faster
    #     # print_collecting_ETA()
    #     # file = str(fileref)
    #     if os.path.isfile(file):
    #         m_files += 1
    #         # print(file)
    #         # todo: use multi-threading to speed up processing of files, split main list into [number of threads] chunks
    #         # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
    #         # todo: maybe optimize cache this way and do binary search using file size - for huge lists of files above 100K it could optimize the search speeds
    #         # todo: one idea to optimize the total run time is to compute the hashes only for files that have same size, but computing hashes of files could be useful for identifying changed files in the future, thus ensuring different versions of same file are also backed up
    #         if len(cached_files):
    #             if file not in [ x["path"] for x in cached_files ]: # todo: figure out if this optimizes or delays script, hoping else branch triggers if cached not provided
    #                 LOGGER.debug("Found uncached file [{}]".format(file))
    #                 item = {'path': file,
    #                         'size': os.path.getsize(file),
    #                         'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
    #                         'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING)
    #                         }
    #                 m_size += item['size']
    #                 items.append(item)
    #             else:
    #                 LOGGER.debug("Skipped already indexed file [{}]".format(file))
    #                 m_cached += 1 # this means file is already indexed so we skip rehashing it
    #                 pass
    #         else:
    #             LOGGER.debug("Caching file [{}]".format(file))
    #             item = {'path': file,
    #                     'size': os.path.getsize(file),
    #                     'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
    #                     'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING) # todo: figure out elevation for files that are in system folders does not work even if console is admin
    #                     }
    #             m_size += item['size']
    #             items.append(item)

    LOGGER.info("Processed [{}/{}] uncached files in [{}] generating [{}] metadata".format(
            m_files - m_cached,
            metric["files"],
            print_time(time.time() - start_time),
            print_size(sys.getsizeof(items))
        ))

    # note: stop the printing thread
    PRINT_FINISHED = True
    print_thread.join()

    return items


@timeit
def collect_all_files(paths=[], hidden=False, metrics=[], cached_files=[], cached_paths=[], parallelize=True):
    """
    :param paths:
    :param hidden:
    :param metrics:
    :param files: files loaded from precached files
    :return:
    """
    start_time = time.time()
    LOGGER.info("Started processing hashes for files from [{}] paths".format( len(paths)) )
    # todo: calculate how much overhead the threading introduces and display it
    # todo: maintain the global variables only in the functions that use them
    global FILES
    FILES = cached_files # note: adding cached files directly to files index
    for path in paths:
        global METRIC
        METRIC = [x for x in metrics if x["path"] == path][0]
        LOGGER.debug("Collecting files in path [{}] which contains [{}] files totaling [{}]".format(path, METRIC["files"], print_size(METRIC["size"])))
        meta = collect_files_in_path(path, hidden, METRIC, cached_files, cached_paths, parallelize)
        LOGGER.debug("Collected files in [%s] and built up [%s] of metadata" % (print_time(time.time() - start_time), print_size(sys.getsizeof(meta))))
        FILES += meta
    FILES.sort(key=lambda x: x["size"]) # note: [comment3] very important to get files sorted
    return FILES


@timeit
def collect_metrics_in_path(path="", hidden=False):
    """
    help: [ https://stackoverflow.com/questions/19747408/how-get-number-of-subfolders-and-folders-using-python-os-walks ]
    :param path:
    :param hidden:
    :return: {files:int, folders:int, size:int}
    """
    # todo: found unused parameter, need to figure out if os.walk traverses hidden folders by default, or folders starting with `.`
    files = []
    folders = 0
    size = 0
    for root, dirs, items in os.walk(path):
        folders += len(dirs)
        for i in items:
            p = os.path.join(root, i)
            # print(p)
            if os.path.isfile(p):
                # files += 1
                files.append(p) # important: [comment2] collecting filepaths, and then iterating through the list increased execution time from `10min` to `16min`
                size += os.path.getsize(p)
            # if os.path.isdir(p):
            #     folders += 1
    return {'path': path, 'files': len(files), 'folders': folders, 'size': size, 'items': files}


@timeit
def collect_all_metrics(paths=[], hidden=False):
    metrics = []
    for path in paths:
        metric = collect_metrics_in_path(path, hidden)
        metrics.append(metric)
        LOGGER.info("Path [{}] contains [{}] folders and [{}] items, totaling [{}]".format(metric["path"], metric["folders"], metric["files"], print_size(metric["size"])))
    return metrics


def print_time(time):
    miliseconds = time * 1000 % 1000
    seconds = time % 60
    time /= 60
    minutes = time % 60
    time /= 60
    hours = time % 24
    time /= 24
    days = time
    return "%ddays %.2d:%.2d:%.2d.%.3d" % (days, hours, minutes, seconds, miliseconds)


def print_size(size):
    bytes = size % 1024
    size /= 1024
    kbytes = size % 1024
    size /= 1024
    mbytes = size % 1024
    size /= 1024
    gbytes = size % 1024
    size /= 1024
    tbytes = size
    return "%.2fTB %.2fGB %.2fMB %.2fKB %.2fB" % (tbytes, gbytes, mbytes, kbytes, bytes)


def menu():
    debug_levels = {'critical': logging.CRITICAL, 'error': logging.ERROR, 'warning': logging.WARNING,
                    'info': logging.INFO, 'debug': logging.DEBUG, 'notset': logging.NOTSET}

    parser = argparse.ArgumentParser(
        description='Find duplicate files in given paths based on file size and checksum validating content is '
                    'similar - chance of different files with same size and checksum should be close to 0')

    # todo: add timeout parameter which is used by the print threads
    parser.add_argument('-p', '--parallelize', default=True, action='store_true', required=False,
                        help='flag indicating if the script should use multi-threading capability, this can add overhead instead of speed things up')
    parser.add_argument('-d', '--debug', choices=debug_levels.keys(), default='info', required=False,
                        help='parameter indicating the level of logs to be shown on screen')
    parser.add_argument('-j', '--json', action='store_true', required=False,
                        help='flag indicating that a json containing duplicate file paths will be generated')
    parser.add_argument('-c', '--cache', action='store_true', required=False,
                        help='flag indicating that a cache file containing the indexes should be generated')
    parser.add_argument('-k', '--kache', required=False,
                        help='parameter containing the path to a cache file to be loaded so the processing of files is faster')
    parser.add_argument('-l', '--links', action='store_true', required=False,
                        help='flag indicating that a symbolic links should be created from duplicate to original file')
    # todo
    # parser.add_argument('-r', '--reverse', action='store_true', required=False,
    #                     help='flag indicating that a symbolic links should be replaced with copies of the original file, useful when restoring a backup')

    parser.add_argument('-e', '--erase', action='store_true', required=False,
                        help='flag indicating that duplicate files will be erased')
    parser.add_argument('-n', '--hidden', action='store_true', required=False,
                        help='flag indicating that python should search for hidden files')
    parser.add_argument('paths', metavar='paths', nargs='+',
                        help='paths where to search through - list of strings separated by space')
    arguments = parser.parse_args()

    # note: patch logging level to objects
    arguments.debug = debug_levels[arguments.debug]

    return arguments


# @timeit # important: adding this decorator drastically reduced performance - it seems like decorator nesting is a 10X performance overhead issue for python
def main():
    start_time = time.time()
    args = menu()

    # note: add a handler for the LOGGER, thus changing the format of the logs
    global LOGGER
    handler = logging.StreamHandler()
    handler.setFormatter(LOG_FORMATTER)
    handler.setLevel(args.debug)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(args.debug)

    cached_files = []
    if args.kache:
        cached_files, cached_paths = load_cache(args.kache)

    metrics = collect_all_metrics(args.paths, args.hidden)
    # todo: implement progressive threading, meaning interrupt single thread and spawn more threads over the remaining data as time progresses
    # todo: implement threading for `collect_all_files` and for `find_duplicates` - which should speed up things
    files = collect_all_files(args.paths, args.hidden, metrics, cached_files, cached_paths, args.parallelize)

    if args.cache:
        dump_cache(files)

    preserve_files = copy.deepcopy(files)
    zero_sized_files = [ x for x in files if x["size"] == 0 ] # todo: need to deal somehow with these files that pollute disks

    global PROCESSED
    PROCESSED = [ False for x in range(len(FILES))]

    # note: duplicates will destructively interfere with FILES and will
    duplicates = find_duplicates(files, args.parallelize)  # todo: figure out how to do in place changes, instead of storing all files metadata for processing

    if args.json:
        dump_duplicates(duplicates)
    if args.links:
        link_back_duplicates(duplicates)
    if args.erase:
        delete_duplicates(duplicates)

    # todo: show progress bar of script based on OS preliminary data,
    #  because for large folders it can take a while and blank screen does not indicate enough feedback
    #
    #  need to pre-index files and folders to figure out size of files and distribution in subfolders, then start the indexing of metadata
    LOGGER.info("Executed script in [{}]".format(print_time(time.time() - start_time)))


if __name__ == "__main__":
    main()
    pass  # used for debug breakpoint