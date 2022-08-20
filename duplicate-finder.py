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

datetime_format = "%Y-%m-%d_%H-%M-%S"
encoding = "ISO-8859-1"  # help: [ https://www.codegrepper.com/code-examples/python/UnicodeDecodeError%3A+%27utf-16-le%27+codec+can%27t+decode+bytes+in+position+60-61%3A+illegal+UTF-16+surrogate ]

# todo: add a way to configure what base units to use, like days, or weeks, TB or PB, which are used in logging


def timeit(f):
    """
    help: [ https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator ]
    :param f:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('>>> func:[{}] took: [{}]'.format(f.__name__, print_time(te-ts)) )
        return result
    return timed


@timeit
def dump_cache(files=[]):
    """
    :param files:
    :return:
    """
    with open("{}_{}".format(datetime.datetime.now().strftime(datetime_format),
                             ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".cache"),
              "w",
              encoding=encoding) as dumpfile:
        dumpfile.write(json.dumps(files, indent=4))

@timeit
def load_cache(file):
    # todo: integrate this with collecting files, if the file is already indexed then its pointless to compute its cache - this could optimize a lot if there are huge files, for which computing the hash takes longer
    #  for a lot of small files its potentially better to no use cache, and have script recompute hashes than double check hash is not computed already
    files = []
    with open(file, "r", encoding=encoding) as readfile:
        files = json.loads(readfile.read())

    # validate that cached files can be found on disk, if not strip the cache of files not found
    for i in range(len(files), 0, -1):
        if not os.path.exists(files[i]["file"]):
            files.pop(i)

    print("Loaded [{}] cached files totaling [{}] metadata".format(len(files), print_size(sys.getsizeof(files))))
    return files


@timeit
def dump_duplicates(files=[]):
    """
    help: [ https://appdividend.com/2022/06/02/how-to-convert-python-list-to-json/ ] - dumping objects to json
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    with open("{}_{}".format(datetime.datetime.now().strftime(datetime_format),
                             ('.').join(os.path.basename(__file__).split('.')[:-1]) + ".json"),
              "w",
              encoding=encoding) as dumpfile:
        dumpfile.write(json.dumps(files, indent=4))


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
            os.link('{}'.format(series[0]["path"]), '{}.lnk'.format(series[i]["path"]))
            # subprocess.call(['mklink', '"{}.lnk"'.format(series[i]["path"]), '"{}"'.format(series[0]["path"])], shell=True) # note: does not have sufficient priviledges


@timeit
def delete_duplicates(files=[]):
    """
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in files:
        for i in range(1, len(series)):
            print("deleting [{}]".format(series[i]["path"]))
            os.remove(series[i]["path"])


@timeit
def find_duplicates(files=[]):
    """
    :param files: [{path:str,size:int,checksum:str}, ...]
    :return: [[original_file, duplicate1, duplicate2, ...], ...]
    """
    m_start_time = time.time()
    print("Started searching for duplicates")
    all_duplicates = []
    m_duplicates = 0
    files.sort(key=lambda x: x["size"])  # sort the files based on size, easier to do comparisons
    for i in range(len(files) - 1):
        duplicates_for_file = [files[i]]  # [comment1]: consider the 0 index of each list as the original file
        for j in range(i + 1, len(files)):
            # print("{} - {}".format(i,j))
            if files[i]["size"] == files[j]["size"] and files[i]["checksum"] == files[j]["checksum"] and files[i]["size"] != 0:
                # todo: figure out what to do with files having size 0, because they can pollute disks as well
                duplicates_for_file.append(files[j])
        if len(duplicates_for_file) > 1:
            duplicates_for_file.sort(key=lambda y: y["time"])  # sort duplicate files, preserving oldest one, improve for [comment1]
            all_duplicates.append(duplicates_for_file)  # based on [comment1], only if a list of duplicates
            m_duplicates += len(duplicates_for_file) - 1
            #  contains more than 1 element, then there are duplicates
    print("Found [{}] duplicated files having [{}] duplicates and totaling [{}] in [{}] generating [{}] metadata".format(
        len(all_duplicates),
        m_duplicates,
        print_size([sum([all_duplicates[i]["size"] for i in range(1, len(x))]) for x in all_duplicates][0] if len(all_duplicates) > 0 else 0),
        print_time(time.time() - m_start_time),
        print_size(sys.getsizeof(all_duplicates))))
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
    for fileref in filter:
        m_files += 1
        if (time.time() - m_start_time) / m_pop_timeout > m_popouts:
            m_popouts += 1
            print("Processed [{}/{}] files in [{}] ETA:[{}] based on [{:.2f}%] data processed generating [{}] metadata".format(
                m_files,
                metric["files"],
                print_time( time.time() - m_start_time ),
                print_time( (metric["size"] - m_size) * (time.time() - m_start_time) / m_size ),
                m_size / metric["size"] * 100,
                print_size( sys.getsizeof(files) )
                ))
        file = str(fileref)
        if os.path.isfile(file):
            # print(file)
            # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
            if len(cached_files):
                if file not in [ x["path"] for x in cached_files ]: # todo: figure out if this optimizes or delays script, hoping else branch triggers if cached not provided
                    item = {'path': file,
                            'size': os.path.getsize(file),
                            'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(datetime_format),
                            'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(encoding)
                            }
                    m_size += item['size']
                    files.append(item)
                else:
                    m_cached += 1 # this means file is already indexed so we skip rehashing it
                    pass
            else:
                item = {'path': file,
                        'size': os.path.getsize(file),
                        'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(datetime_format),
                        'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(encoding) # todo: figure out elevation for files that are in system folders does not work even if console is admin
                        }
                m_size += item['size']
                files.append(item)
    print("Processed [{}/{}] uncached files in [{}] generating [{}] metadata".format(
            m_files - m_cached,
            metric["files"],
            print_time(time.time() - m_start_time),
            print_size(sys.getsizeof(files))
        ))
    return files


def collect_all_files(paths=[], hidden=False, metrics=[], cached_files=[]):
    """
    :param paths:
    :param hidden:
    :param metrics:
    :param files: files loaded from precached files
    :return:
    """
    files = cached_files # note: adding cached files directly to files index
    for path in paths:
        m_start_time = time.time()
        metric = [x for x in metrics if x["path"] == path][0]
        print("Collecting files in path [{}] which contains [{}] files totaling [{}]".format(path, metric["files"], print_size(metric["size"])))
        meta = collect_files_in_path(path, hidden, metric, cached_files)
        print("Collected files in [%s] and built up [%s] of metadata" % (print_time(time.time() - m_start_time), print_size(sys.getsizeof(meta))))
        files += meta
    return files


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
        files += len(items)
        folders += len(dirs)
        for i in items:
            p = os.path.join(root, i)
            # print(p)
            if os.path.isfile(p):
                size += os.path.getsize(p)
    return {'path': path, 'files': files, 'folders': folders, 'size': size}


def collect_all_metrics(paths=[], hidden=False):
    metrics = []
    for path in paths:
        m_start_time = time.time()
        print("Collecting metrics for path [{}]".format(path))
        metric = collect_metrics_in_path(path, hidden)
        metrics.append(metric)
        print("Path [{}] contains [{}] folders and [{}] items, totaling [{}]".format(metric["path"], metric["folders"], metric["files"], print_size(metric["size"])))
        print("Collected metrics in [%.2f] seconds" % (time.time() - m_start_time))
    return metrics


def print_time(time):
    seconds = time % 60
    time /= 60
    minutes = time % 60
    time /= 60
    hours = time % 24
    time /= 24
    days = time
    return "%ddays %.2d:%.2d:%.2d" % (days, hours, minutes, seconds)


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


def show_menu():
    parser = argparse.ArgumentParser(
        description='Find duplicate files in given paths based on file size and checksum validating content is '
                    'similar - chance of different files with same size and checksum should be close to 0')
    parser.add_argument('-j', '--json', action='store_true', required=False,
                        help='flag indicating that a json containing duplicate file paths will be generated')
    parser.add_argument('-c', '--cache', action='store_true', required=False,
                        help='flag indicating that a cache file containing the indexes should be generated')
    parser.add_argument('-k', '--kache', required=False,
                        help='parameter containing the path to a cache file to be loaded so the processing of files is faster')
    parser.add_argument('-l', '--links', action='store_true', required=False,
                        help='flag indicating that a symbolic links should be created from duplicate to original file')
    parser.add_argument('-e', '--erase', action='store_true', required=False,
                        help='flag indicating that duplicate files will be erased')
    parser.add_argument('-n', '--hidden', action='store_true', required=False,
                        help='flag indicating that python should search for hidden files')
    parser.add_argument('paths', metavar='paths', nargs='+', help='paths where to search through - list of strings '
                                                                  'separated by space')
    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    args = show_menu()

    cached_files = []
    if args.kache:
        cached_files = load_cache(args.kache) # todo: loading precomputed index file does not guarantee all files are indexed, will have to re-hash files not present

    metrics = collect_all_metrics(args.paths, args.hidden)

    files = collect_all_files(args.paths, args.hidden, metrics, cached_files)  # todo: add some timeit wrappers around these calls which can take a while for large systems
    duplicates = find_duplicates(files)  # todo: figure out how to do in place changes, instead of storing all files metadata for processing

    if args.cache:
        dump_cache(files)
    if args.json:
        dump_duplicates(duplicates)
    if args.links:
        link_back_duplicates(duplicates)
    if args.erase:
        delete_duplicates(duplicates)

    # todo: add some metrics, how many duplicate files were found out of how many files were traversed and indexed,
    #  how much metadata was generated, and how much disk size was processed, how much time it took,
    #  percentage of duplicate files found out of all files indexed

    # todo: show progress bar of script based on OS preliminary data,
    #  because for large folders it can take a while and blank screen does not indicate enough feedback
    #
    #  need to pre-index files and folders to figure out size of files and distribution in subfolders, then start the indexing of metadata

    pass  # used for debug breakpoint
