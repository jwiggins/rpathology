import os.path as op
import re
import subprocess
import sys

from elftools.common.exceptions import ELFError
from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile

PY3K = sys.version_info > (3, 0)
MISSING_LIB_REGEX = re.compile(r'.+(not found).+')


def _bytes2str(b):
    if PY3K:
        return b.decode('utf-8')
    else:
        return b


def _elf_type(path):
    with open(path, 'rb') as fp:
        elf = ELFFile(fp)
        return elf.header['e_type']


def _get_missing_libraries(path):
    """ Shell out to ldd to get the library references that can't be resolved.
    """
    cmdline = ["ldd", path]
    p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)

    missing = []
    try:
        outs, _ = p.communicate()
        outs = _bytes2str(outs)
        for line in outs.split('\n'):
            if MISSING_LIB_REGEX.match(line):
                libname = line.split('=>')[0].strip()
                missing.append(libname)
    except subprocess.TimeoutExpired:
        p.kill()

    return missing


def build_rpath(root, lib_dir, file_path):
    """ Constructs an RPATH for a file.
    """
    parts = ['$ORIGIN']
    moves = [op.relpath(root, op.dirname(file_path)),
             op.relpath(lib_dir, root)]
    parts.extend([m for m in moves if m != '.'])
    return op.join(*parts)


def is_executable(path):
    """ Returns True if a file is an ELF file
    """
    try:
        with open(path, 'rb') as fp:
            ELFFile(fp)
        return True
    except ELFError:
        return False


def get_missing_libraries(path):
    """ Return a list of missing libraries for a given executable.
    """
    if not is_executable(path):
        return []

    return _get_missing_libraries(path)


def get_rpaths(path):
    """ Get all the RPATH and RUNPATH entries for an ELF binary
    """
    rpaths = []
    with open(path, 'rb') as fp:
        elf = ELFFile(fp)
        for section in elf.iter_sections():
            if isinstance(section, DynamicSection):
                for tag in section.iter_tags():
                    d_tag = tag.entry.d_tag
                    if d_tag == 'DT_RPATH':
                        rpaths.extend(tag.rpath.split(':'))
                    elif d_tag == 'DT_RUNPATH':
                        rpaths.extend(tag.runpath.split(':'))
    return rpaths


def set_rpaths(path, rpaths):
    """ Set the RPATH for an ELF binary by shelling out to patchelf.
    """
    rpaths = ":".join(rpaths)
    cmdline = ["patchelf", "--set-rpath", rpaths, path]
    subprocess.check_call(cmdline)
