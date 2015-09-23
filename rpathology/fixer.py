from __future__ import print_function

import argparse
from functools import partial
import glob
import os
import os.path as op

from .elf import is_elf, get_rpaths, set_rpaths


def visit_hierarchy(path, file_glob, visitor, **kwargs):
    """ Walk a directory hierarchy and call a function for each file whose name
    matches a given pattern.
    """
    for root, _, files in os.walk(path):
        for fn in glob.fnmatch.filter(files, file_glob):
            visitor(op.join(root, fn), **kwargs)


def fix_rpaths(root, lib_dirs, path, append=False):
    """ Change the RPATH entry for a single executable.
    """
    if not is_elf(path):
        print('{} is not an ELF file!'.format(path))
        return

    def build_rpath(lib_dir, file_path):
        parts = ['$ORIGIN']
        moves = [op.relpath(root, op.dirname(file_path)),
                 op.relpath(lib_dir, root)]
        parts.extend([m for m in moves if m != '.'])
        return op.join(*parts)

    rpaths = get_rpaths(path)
    if len(rpaths) > 0:
        new_rpaths = [build_rpath(ld, path) for ld in lib_dirs]
        if append:
            new_rpaths = rpaths + new_rpaths

        set_rpaths(path, new_rpaths)


def main():
    description = 'Fix the RPATH for all executables in a directory hierarchy'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.HelpFormatter)
    parser.add_argument('--file-glob', '-f', default='*',
                        help='The glob used to locate executables.')
    parser.add_argument('--lib-dir', '-l', required=True, action='append',
                        help=('The directory where libraries are located. '
                              'This option can be supplied multiple times.'))
    parser.add_argument('--executable-root', '-e', required=True,
                        help='The root directory of the executables.')
    parser.add_argument('--append', '-a', action='store_true',
                        help='Append new RPATH to existing RPATH.')
    args = parser.parse_args()

    exe_root = op.abspath(op.normpath(args.executable_root))
    lib_dirs = [op.abspath(op.normpath(d)) for d in args.lib_dir]
    visitor = partial(fix_rpaths, exe_root, lib_dirs)
    visit_hierarchy(exe_root, args.file_glob, visitor, append=args.append)


if __name__ == '__main__':
    main()
