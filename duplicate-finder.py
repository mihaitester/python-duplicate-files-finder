import argparse
import glob
import os
import hashlib

files = []


def process_files_in_path(path=""):
    for file in glob.glob(path + "/*"):
        if os.path.isfile(file):
            # print(file)
            # todo: ideally build a tree for faster searches and index files based on size - do binary search over it
            files.append({'path': file,
                          'size': os.path.getsize(file),
                          'checksum': hashlib.md5(open(file, 'rb').read()).digest()
                          })
    files.sort(key=lambda x: x["size"])


def iterate_paths(paths=[]):
    for path in paths:
        process_files_in_path(path)


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
    iterate_paths(args.paths)
    pass  # used for debug breakpoint
