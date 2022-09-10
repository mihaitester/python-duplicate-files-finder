import argparse
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

# use global parameters
m_start_time = time.time()
m_popouts = 0
m_files = 0
m_size = 1 # avoid division by 0
m_cached = 0
m_finished = False

# need to have this global
metrics = []
metric = []
files = []


def print_collecting_ETA(timeout):
    global m_start_time, m_popouts, m_files, metric, m_size
    if (time.time() - m_start_time) / timeout > m_popouts:
        m_popouts += 1
        LOGGER.info("Processed [{}/{}] files in [{}] ETA:[{}] based on [{:.2f}%] data processed generating [{}] metadata".format(
                m_files,
                metric["files"],
                print_time(time.time() - m_start_time),
                print_time((metric["size"] - m_size) * (time.time() - m_start_time) / m_size),
                m_size / metric["size"] * 100,
                print_size(sys.getsizeof(files))
            ))


i = 0
def print_duplicates_ETA(timeout):
    global m_start_time, m_popouts, i, files
    if (time.time() - m_start_time) / timeout > m_popouts:
        # print("Compared [{}/{}] files in [{}] ETA: [{}]".format(i+1, len(files), print_time(time.time()-m_start_time), print_time( ( len(files)-i ) * (time.time() - m_start_time) / len(files) )))
        done_comparisons = int((i + 1) * len(files) / 2)
        total_comparisons = int(len(files) * (len(files) + 1) / 2)
        m_popouts += 1
        LOGGER.info(
            "Done [{}/{}] comparisons, comparing [{}/{}] files in [{}] ETA: [{}] based on [{:.2f}%] comparisons".format(
                done_comparisons,
                total_comparisons,
                i + 1,
                len(files),
                print_time(time.time() - m_start_time),
                print_time((total_comparisons - done_comparisons) * (time.time() - m_start_time) / done_comparisons),
                # todo: fix this approximation, need to use comparisons as base number instead of files
                done_comparisons / total_comparisons * 100))


def thread_print(function=print_collecting_ETA, timeout=60, micro=2):
    # help: [ https://stackoverflow.com/questions/8600161/executing-periodic-actions ] - every timeout print out current progress
    # help: [ https://superfastpython.com/thread-share-variables/ ] - how to share data with the printing thread
    # help: [ https://docs.python.org/3/library/threading.html ] - basics of python threading
    # help: [ https://stackoverflow.com/questions/3221655/python-threading-string-arguments ] - pass arguments to thread
    # help: [ https://www.geeksforgeeks.org/passing-function-as-an-argument-in-python/ ] - sending print function as parameter
    while True:
        function(timeout)
        # note: instead of waiting the full timeout use micro sleeps and check if mainthread finished in the meantime
        for i in range(int(timeout/micro)):
            if m_finished:
                return
            time.sleep(micro)


@timeit
def dump_cache(files=[]):
    """
    :param files:
    :return:
    """
    cache_file = "{}_{}".format(datetime.datetime.now().strftime(DATETIME_FORMAT),
                                ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".cache")
    try:
        LOGGER.info("Dumping cache [{}]".format(cache_file))
        with open(cache_file, "w", encoding=ENCODING) as dumpfile:
            dumpfile.write(json.dumps(files, indent=4))
        LOGGER.debug("Dumped cache [{}]".format(cache_file))
    except Exception as ex:
        LOGGER.error("Failed to dump cache [{}] with exception [{}]".format(cache_file), ex.message)


@timeit
def load_cache(cache_file=""):
    # todo: integrate this with collecting files, if the file is already indexed then its pointless to compute its cache - this could optimize a lot if there are huge files, for which computing the hash takes longer
    #  for a lot of small files its potentially better to no use cache, and have script recompute hashes than double check hash is not computed already
    files = []
    try:
        LOGGER.info("Loading cache [{}]".format(cache_file))
        with open(cache_file, "r", encoding=ENCODING) as readfile:
            files = json.loads(readfile.read())
        LOGGER.debug("Loaded cache [{}]".format(cache_file))
    except Exception as ex:
        LOGGER.error("Failed to load cache [{}] with exception [{}]".format(cache_file, str(ex)))

    # validate that cached files can be found on disk, if not strip the cache of files not found
    LOGGER.debug("Stripping files from cache")
    loaded_files = len(files)
    for i in range(len(files)-1, 0, -1):
        if not os.path.exists(files[i]["path"]):
                files.pop(i)
    LOGGER.debug("Stripped [{}] files from cache that are not on disk".format(loaded_files - len(files)))

    LOGGER.info("Loaded [{}] cached files totaling [{}] metadata".format(len(files), print_size(sys.getsizeof(files))))
    return files


@timeit
def dump_duplicates(files=[]):
    """
    help: [ https://appdividend.com/2022/06/02/how-to-convert-python-list-to-json/ ] - dumping objects to json
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    duplicates_file = "{}_{}".format(datetime.datetime.now().strftime(DATETIME_FORMAT),
                                    ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".json")
    try:
        LOGGER.info("Dumping duplicates file [{}]".format(duplicates_file))
        with open(duplicates_file, "w", encoding=ENCODING) as dumpfile:
            dumpfile.write(json.dumps(files, indent=4))
        LOGGER.debug("Dumped duplicates file [{}]".format(duplicates_file))
    except Exception as ex:
        LOGGER.error("Failed to dump duplicates file [{}] with exception [{}]".format(duplicates_file, ex.message))


@timeit
def link_back_duplicates(files=[]):
    """
    help: [ https://stackoverflow.com/questions/1447575/symlinks-on-windows ]
    help: [ https://pypi.org/project/pywin32/ ]
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in files:
        for i in range(1, len(series)):
            try:
                LOGGER.info("Linking [{}] to file [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"]))
                os.link('{}'.format(series[0]["path"]), '{}.lnk'.format(series[i]["path"]))
                LOGGER.debug("Linked [{}] to file [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"]))
                # subprocess.call(['mklink', '"{}.lnk"'.format(series[i]["path"]), '"{}"'.format(series[0]["path"])], shell=True) # note: does not have sufficient priviledges
            except Exception as ex:
                LOGGER.error("Failed linking [{}] to file [{}] with exception [{}]", '{}.lnk'.format(series[i]["path"], series[0]["path"], ex.message))

@timeit
def delete_duplicates(files=[]):
    """
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in files:
        for i in range(1, len(series)):
            try:
                LOGGER.info("Deleting [{}]".format(series[i]["path"]))
                os.remove(series[i]["path"])
                LOGGER.debug("Deleted [{}]".format(series[i]["path"]))
            except Exception as ex:
                LOGGER.error("Failed to delete [{}] with exception [{}]".format(series[i]["path"], ex.message))


@timeit
def find_duplicates(items=[], m_pop_timeout=60):
    """
    :param files: [{path:str,size:int,checksum:str}, ...]
    :return: [[original_file, duplicate1, duplicate2, ...], ...]
    """
    LOGGER.info("Started searching for duplicates among [{}] indexed files".format( len(items)) )
    global m_start_time, files, m_finished, m_popouts, i
    all_duplicates = []
    m_start_time = time.time()
    m_duplicates = 0
    files = items
    files.sort(key=lambda x: x["size"])  # sort the files based on size, easier to do comparisons
    m_processed = 0
    m_popouts = 0

    m_finished = False
    t = threading.Thread(target=thread_print, args=[print_duplicates_ETA, m_pop_timeout])  # pass the timeout on start of thread
    t.daemon = True
    t.start()

    for i in range(len(files) - 1):
        # print_duplicates_ETA()
        # todo: optimize search, by comparing only files that have the same size, which would run faster
        duplicates_for_file = [files[i]]  # [comment1]: consider the 0 index of each list as the original file
        for j in range(i + 1, len(files)):
            # print("{} - {}".format(i,j))
            if files[i]["size"] == files[j]["size"] and files[i]["checksum"] == files[j]["checksum"] and files[i]["size"] != 0:
                LOGGER.debug("Found duplicate [{}] for file [{}]".format(files[j]["path"], files[i]["path"]))
                duplicates_for_file.append(files[j])
            else:
                if files[i]["size"] == 0:
                    # todo: figure out what to do with files having size 0, because they can pollute disks as well
                    LOGGER.debug("Found empty file [{}]".format(files[i]["path"]))
        if len(duplicates_for_file) > 1:
            LOGGER.debug("Found total [{}] duplicates for file [{}]".format(len(duplicates_for_file)-1, files[i]["path"]))
            duplicates_for_file.sort(key=lambda y: y["time"])  # sort duplicate files, preserving oldest one, improve for [comment1]
            all_duplicates.append(duplicates_for_file)  # based on [comment1], only if a list of duplicates contains more than 1 element, then there are duplicates
            m_duplicates += len(duplicates_for_file) - 1 # based on [comment1], first item in a sequence of duplicates is an original

    LOGGER.info("Found [{}] duplicated files having [{}] duplicates and occupying [{}] out of [{}] in [{}] generating [{}] metadata".format(
        len(all_duplicates),
        m_duplicates,
        print_size(sum([sum([x[i]["size"] for i in range(1, len(x))]) for x in all_duplicates]) if len(all_duplicates) > 0 else 0),
        print_size(sum([x["size"] for x in files])),
        print_time(time.time() - m_start_time),
        print_size(sys.getsizeof(all_duplicates))))
    m_finished = True
    t.join()
    return all_duplicates


def collect_files_in_path(path="", hidden=False, metric={}, cached_files=[], m_pop_timeout=60):
    """
    help: [ https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times ] - use the proper time flag
    help: [ https://stackoverflow.com/questions/49047402/python-3-6-glob-include-hidden-files-and-folders ] - glob no longer includes all files
    :param path:
    :param hidden: flag indicating if searching through hidden files
    :param files: list of files that have been pre-cached, should improve performance
    :return:
    """
    global files, m_start_time, m_popouts, m_files, m_size, m_cached, m_finished # need this for the printing thread
    files = []
    filter = pathlib.Path(path).glob('**/*')  # get hidden files
    if hidden != True:
        filter = glob.glob(os.path.join(path, "**/*"), recursive=True) + \
                 glob.glob(os.path.join(path, ".**/*"), recursive=True)  # get recursively inside folders

    m_start_time = time.time()
    m_popouts = 0
    m_files = 0
    m_size = 1 # avoid division by 0
    m_cached = 0

    m_finished = False
    t = threading.Thread(target=thread_print, args=[print_collecting_ETA, m_pop_timeout]) # pass the timeout on start of thread
    t.daemon = True
    t.start()

    for fileref in filter:
        # print_collecting_ETA()
        file = str(fileref)
        if os.path.isfile(file):
            m_files += 1
            # print(file)
            # todo: use multi-threading to speed up processing of files, split main list into [number of threads] chunks
            # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
            # todo: maybe optimize cache this way and do binary search using file size - for huge lists of files above 100K it could optimize the search speeds
            # todo: one idea to optimize the total run time is to compute the hashes only for files that have same size, but computing hashes of files could be useful for identifying changed files in the future, thus ensuring different versions of same file are also backed up
            if len(cached_files):
                if file not in [ x["path"] for x in cached_files ]: # todo: figure out if this optimizes or delays script, hoping else branch triggers if cached not provided
                    LOGGER.debug("Found uncached file [{}]".format(file))
                    item = {'path': file,
                            'size': os.path.getsize(file),
                            'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
                            'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING)
                            }
                    m_size += item['size']
                    files.append(item)
                else:
                    LOGGER.debug("Skipped already indexed file [{}]".format(file))
                    m_cached += 1 # this means file is already indexed so we skip rehashing it
                    pass
            else:
                LOGGER.debug("Caching file [{}]".format(file))
                item = {'path': file,
                        'size': os.path.getsize(file),
                        'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(DATETIME_FORMAT),
                        'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(ENCODING) # todo: figure out elevation for files that are in system folders does not work even if console is admin
                        }
                m_size += item['size']
                files.append(item)
    LOGGER.info("Processed [{}/{}] uncached files in [{}] generating [{}] metadata".format(
            m_files - m_cached,
            metric["files"],
            print_time(time.time() - m_start_time),
            print_size(sys.getsizeof(files))
        ))

    m_finished = True
    t.join()
    return files




def collect_all_files(paths=[], hidden=False, metrics=[], cached_files=[]):
    """
    :param paths:
    :param hidden:
    :param metrics:
    :param files: files loaded from precached files
    :return:
    """
    LOGGER.info("Started processing hashes for files from [{}] paths".format( len(paths)) )
    files = cached_files # note: adding cached files directly to files index
    for path in paths:
        global metric
        metric = [x for x in metrics if x["path"] == path][0]
        LOGGER.debug("Collecting files in path [{}] which contains [{}] files totaling [{}]".format(path, metric["files"], print_size(metric["size"])))
        meta = collect_files_in_path(path, hidden, metric, cached_files)
        LOGGER.debug("Collected files in [%s] and built up [%s] of metadata" % (print_time(time.time() - m_start_time), print_size(sys.getsizeof(meta))))
        files += meta
    return files


@timeit
def collect_metrics_in_path(path="", hidden=False):
    """
    help: [ https://stackoverflow.com/questions/19747408/how-get-number-of-subfolders-and-folders-using-python-os-walks ]
    :param path:
    :param hidden:
    :return: {files:int, folders:int, size:int}
    """
    # todo: found unused parameter, need to figure out if os.walk traverses hidden folders by default, or folders starting with `.`
    files = 0
    folders = 0
    size = 0
    for root, dirs, items in os.walk(path):
        folders += len(dirs)
        for i in items:
            p = os.path.join(root, i)
            # print(p)
            if os.path.isfile(p):
                files += 1
                size += os.path.getsize(p)
            # if os.path.isdir(p):
            #     folders += 1
    return {'path': path, 'files': files, 'folders': folders, 'size': size}


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
    parser = argparse.ArgumentParser(
        description='Find duplicate files in given paths based on file size and checksum validating content is '
                    'similar - chance of different files with same size and checksum should be close to 0')

    parser.add_argument('-d', '--debug', choices=['critical', 'error', 'warning', 'info', 'debug', 'notset'],
                        default='info', required=False,
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
    parser.add_argument('paths', metavar='paths', nargs='+', help='paths where to search through - list of strings '
                                                                  'separated by space')
    arguments = parser.parse_args()

    # patch logging level to objects
    debug_levels = {'critical': logging.CRITICAL, 'error': logging.ERROR, 'warning': logging.WARNING, 'info': logging.INFO, 'debug': logging.DEBUG, 'notset': logging.NOTSET}
    arguments.debug = debug_levels[arguments.debug]

    return arguments


if __name__ == "__main__":
    args = menu()

    # note: add a handler for the LOGGER, thus changing the format of the logs
    handler = logging.StreamHandler()
    handler.setFormatter(LOG_FORMATTER)
    handler.setLevel(args.debug)
    LOGGER.addHandler(handler)

    LOGGER.setLevel(args.debug)

    cached_files = []
    if args.kache:
        cached_files = load_cache(args.kache)

    metrics = collect_all_metrics(args.paths, args.hidden)
    files = collect_all_files(args.paths, args.hidden, metrics, cached_files)

    if args.cache:
        dump_cache(files)

    duplicates = find_duplicates(files) # todo: figure out how to do in place changes, instead of storing all files metadata for processing

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


    pass  # used for debug breakpoint
