from __future__ import print_function

import argparse
import glob
import os
import os.path as op

from .api import is_executable, get_rpaths


def show_rpaths(path):
    """ Change the RPATH entry for a single executable.
    """
    shortpath = op.basename(path)
    if not is_executable(path):
        print('{} is not an executable file!'.format(shortpath))
        return

    rpaths = get_rpaths(path)
    if len(rpaths) > 0:
        print('{}: {}'.format(shortpath, ', '.join(rpaths)))


def walk_hierarchy(path, file_glob):
    """ Walk a directory hierarchy and call a function for each file whose name
    matches a given pattern.
    """
    for root, _, files in os.walk(path):
        for i, fn in enumerate(glob.fnmatch.filter(files, file_glob)):
            if i == 0:
                print('\nDirectory: {}'.format(root))
            show_rpaths(op.join(root, fn))


def main():
    description = 'Show the RPATH for all executables in a directory hierarchy'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.HelpFormatter)
    parser.add_argument('--file-glob', '-g', default='*',
                        help='The glob used to locate executables.')
    parser.add_argument('--directory', '-d', required=True,
                        help='The root directory of the executables.')
    args = parser.parse_args()

    walk_hierarchy(op.abspath(args.directory), args.file_glob)


if __name__ == '__main__':
    main()
