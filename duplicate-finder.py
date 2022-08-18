import argparse
import glob
import os
import hashlib


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


def process_all_files(files):
    duplicates = []
    files.sort(key=lambda x: x["size"])  # sort the files based on size, easier to do comparisons
    # todo: once the files are sorted based on size, loop similar sized files and if they match create a new list of files containing duplicates
    return duplicates


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
    duplicates = process_all_files(files)
    pass  # used for debug breakpoint
