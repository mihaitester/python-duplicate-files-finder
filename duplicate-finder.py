import argparse


def show_menu():
    parser = argparse.ArgumentParser(
        description='Find duplicate files in given paths based on file size and checksum validating content is '
                    'similar - chance of different files with same size and checksum should be close to 0')
    parser.add_argument('paths', metavar='paths', nargs='+', help='paths where to search through - list of strings '
                                                                  'sepparated by space')

    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    args = show_menu()
    pass