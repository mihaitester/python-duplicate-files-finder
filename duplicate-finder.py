import argparse
import glob
import os
import hashlib


def delete_duplicates(files=[]):
    """
    :param files: [[original_file, duplicate1, duplicate2, ...], ...]
    :return:
    """
    for series in files:
        for i in range(1, len(series)):
            print("deleting [{}]".format(series[i]["path"]))
            os.remove(series[i]["path"])


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
    files = []
    for file in glob.glob(path + "/*"):
        if os.path.isfile(file):
            # print(file)
            # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
            files.append({'path': file,
                          'size': os.path.getsize(file),
                          'checksum': hashlib.md5(open(file, 'rb').read()).digest()
                          })
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
    parser.add_argument('paths', metavar='paths', nargs='+', help='paths where to search through - list of strings '
                                                                  'separated by space')

    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    args = show_menu()
    files = collect_all_files(args.paths)
    duplicates = find_duplicates(files)
    # todo: need to do something with the duplicates, either dump a json, or start deleting them
    delete_duplicates(duplicates)
    pass  # used for debug breakpoint
