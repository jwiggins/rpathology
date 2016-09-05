from __future__ import print_function

import argparse
from functools import partial
import glob
import os
import os.path as op

from .api import build_rpath, is_executable, get_rpaths, set_rpaths


def visit_hierarchy(path, file_glob, visitor, **kwargs):
    """ Walk a directory hierarchy and call a function for each file whose name
    matches a given pattern.
    """
    for root, _, files in os.walk(path):
        for fn in glob.fnmatch.filter(files, file_glob):
            visitor(op.join(root, fn), **kwargs)


def fix_rpaths(root, lib_dirs, path, append=False, force=False):
    """ Change the RPATH entry for a single executable.
    """
    if not is_executable(path):
        print('{} is not an executable file!'.format(path))
        return

    rpaths = get_rpaths(path)
    if force or len(rpaths) > 0:
        new_rpaths = [build_rpath(root, ld, path) for ld in lib_dirs]
        if append:
            new_rpaths = rpaths + new_rpaths

        set_rpaths(path, new_rpaths)


def main():
    description = 'Fix the RPATH for all executables in a directory hierarchy'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.HelpFormatter)
    parser.add_argument('--file-glob', '-g', default='*',
                        help='The glob used to locate executables.')
    parser.add_argument('--lib-dir', '-l', required=True, action='append',
                        help=('The directory where libraries are located. '
                              'This option can be supplied multiple times.'))
    parser.add_argument('--directory', '-d', required=True,
                        help='The root directory of the executables.')
    parser.add_argument('--append', '-a', action='store_true',
                        help='Append new RPATH to existing RPATH.')
    parser.add_argument('--force', '-f', action='store_true',
                        help=('Add an RPATH to files even if there previously '
                              'was not one.'))
    args = parser.parse_args()

    exe_root = op.abspath(op.normpath(args.directory))
    lib_dirs = [op.abspath(op.normpath(d)) for d in args.lib_dir]
    visitor = partial(fix_rpaths, exe_root, lib_dirs)
    visit_hierarchy(exe_root, args.file_glob, visitor,
                    append=args.append, force=args.force)


if __name__ == '__main__':
    main()
