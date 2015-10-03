import os.path as op

from machotools.detect import is_macho
from machotools.macho_rewriter import rewriter_factory

LOADER_PATH = '@loader_path'


def build_rpath(root, lib_dir, file_path):
    """ Constructs an RPATH for a file.
    """
    parts = [LOADER_PATH]
    moves = [op.relpath(root, op.dirname(file_path)),
             op.relpath(lib_dir, root)]
    parts.extend([m for m in moves if m != '.'])
    return op.join(*parts)


def is_executable(path):
    """ Returns True if a file is a mach-o file
    """
    return is_macho(path)


def get_missing_libraries(path):
    """ Return a list of missing libraries for a given executable.
    """
    missing = []
    loader_path = op.dirname(path)
    rewriter = rewriter_factory(path)
    for dependency in rewriter.dependencies:
        if dependency.startswith(LOADER_PATH):
            dependency = loader_path + dependency[len(LOADER_PATH):]
        if not op.exists(dependency):
            missing.append(op.basename(dependency))
    return missing


def get_rpaths(path):
    """ Get all the RPATH entries for a mach-o file.
    """
    rewriter = rewriter_factory(path)
    rpaths = [p for p in rewriter.rpaths]
    return rpaths


def set_rpaths(path, rpaths):
    """ Set the RPATHs for a mach-o file.

    XXX: It looks like machotools always appends paths.
    """
    with rewriter_factory(path) as rewriter:
        rewriter.extend_rpaths(rpaths)
