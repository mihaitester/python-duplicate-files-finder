import argparse
import glob
import os


def process_files_in_path(path=""):
    for file in glob.glob(path+"/*"):
        if os.path.isfile(file):
            print(file)


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
    pass # used for debug breakpoint
