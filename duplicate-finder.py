import argparse
import glob
import os
import hashlib
import datetime
import json

datetime_format = "%Y-%m-%d_%H-%M-%S"
encoding = "utf-16"

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


def delete_duplicates(files=[]):
    """
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in files:
        for i in range(1, len(series)):
            print("deleting [{}]".format(series[i]["path"]))
            os.remove(series[i]["path"])  # todo: this will remove the oldest files first, need to figure out fix


def find_duplicates(files=[]):
    """
    :param files: [{path:str,size:int,checksum:str}, ...]
    :return: [[original_file, duplicate1, duplicate2, ...], ...]
    """
    all_duplicates = []
    files.sort(key=lambda x: x["size"])  # sort the files based on size, easier to do comparisons
    # todo: once the files are sorted based on size, loop similar sized files and if they match create a new
    #  list of files containing duplicates
    for i in range(len(files) - 1):
        duplicates_for_file = [files[i]]  # consider the 0 index of each list as the original file
        for j in range(i + 1, len(files)):
            # print("{} - {}".format(i,j))
            if files[i]["size"] == files[j]["size"] and files[i]["checksum"] == files[j]["checksum"]:
                # todo: ideally reference the oldest file and build a list of duplicate paths for that one
                duplicates_for_file.append(files[j])
        if len(duplicates_for_file) > 1:
            all_duplicates.append(duplicates_for_file)  # based on previous comment, only if a list of duplicates
            #  contains more than 1 element, then there are duplicates
    return all_duplicates


def collect_files_in_path(path=""):
    """
    help: [ https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times ] - use the proper time flag
    :param path:
    :return:
    """
    files = []
    for file in glob.glob(path + "/*"): # todo: fix, this line to get recursively into paths
        if os.path.isfile(file):
            # print(file)
            # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
            item = {'path': file,
                    'size': os.path.getsize(file),
                    'time': datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(datetime_format),
                    'checksum': hashlib.md5(open(file, 'rb').read()).digest().decode(encoding)
                    }
            files.append(item)
    return files


def collect_all_files(paths=[]):
    files = []
    for path in paths:
        files += collect_files_in_path(path)
    return files


def show_menu():
    parser = argparse.ArgumentParser(
        description='Find duplicate files in given paths based on file size and checksum validating content is '
                    'similar - chance of different files with same size and checksum should be close to 0')
    parser.add_argument('-j', '--json', action='store_true',
                        help='flag indicating that a json containing duplicate file paths will be generated')
    parser.add_argument('-e', '--erase', action='store_true',
                        help='flag indicating that duplicate files will be erased')
    parser.add_argument('paths', metavar='paths', nargs='+', help='paths where to search through - list of strings '
                                                                  'separated by space')
    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    args = show_menu()
    files = collect_all_files(args.paths)
    duplicates = find_duplicates(files)

    if args.json:
        dump_duplicates(duplicates)
    if args.erase:
        delete_duplicates(duplicates)

    pass  # used for debug breakpoint
