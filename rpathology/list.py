from __future__ import print_function

import argparse
import glob
import os
import os.path as op

from .api import get_missing_libraries


def _show_misses(misses, root):
    print('Directory:', root)
    for path, missing in misses:
        libs = ', '.join(missing)
        print('{} is missing: {}'.format(op.basename(path), libs))
    print()


def walk_hierarchy(path, file_glob):
    """ Walk a directory hierarchy and check each file whose name matches a
    given pattern for missing library references.
    """
    for root, _, files in os.walk(path):
        misses = []
        for fn in glob.fnmatch.filter(files, file_glob):
            p = op.join(root, fn)
            miss = get_missing_libraries(p)
            if miss:
                misses.append((p, miss))

        if len(misses) > 0:
            _show_misses(misses, root)


def main():
    description = ('Show missing libraries for all executables in a directory '
                   'hierarchy')
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
