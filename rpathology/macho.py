from __future__ import print_function

import os.path as op
import subprocess

from .compat import bytes2str

LOADER_PATH = '@loader_path'
RPATH = '@rpath'
HEADER_MAGIC = {
    b'\xce\xfa\xed\xfe': 'MachO-i386',
    b'\xfe\xed\xfa\xce': 'MachO-ppc',
    b'\xfe\xed\xfa\xcf': 'MachO-ppc64',
    b'\xca\xfe\xba\xbe': 'MachO-universal',
    b'\xcf\xfa\xed\xfe': 'MachO-x86_64',
}


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
    with open(path, 'rb') as fi:
        magic = fi.read(4)
    return bool(magic in HEADER_MAGIC)


def get_missing_libraries(path):
    """ Return a list of missing libraries for a given executable.
    """
    missing = []
    loader_path = op.dirname(path)

    def replace_loader_path(s):
        if s.startswith(LOADER_PATH):
            return loader_path + s[len(LOADER_PATH):]
        return s

    rpaths = [replace_loader_path(rpth) for rpth in get_rpaths(path)]
    for dependency in _get_libraries(path):
        dependency = replace_loader_path(dependency)
        if dependency.startswith(RPATH):
            dependency = rpaths[0] + dependency[len(RPATH):]
        if not op.exists(dependency):
            missing.append(op.basename(dependency))
    return missing


def get_rpaths(path):
    """ Get all the RPATH entries for a mach-o file.
    """
    rpaths = []
    for load in _iter_specific_load_commands(path, 'LC_RPATH'):
        name = load.get('path', ' ').split(' ', 1)[0]
        if name:
            rpaths.append(name)
    return rpaths


def make_library_loads_relative(path, prefix):
    """ Rewrite all LC_LOAD_DYLIB commands in a given executable at `path` with
    names starting with `prefix` to @rpath<... everything after prefix>
    """
    if prefix[-1] == '/':
        prefix = prefix[:-1]
    prefix_len = len(prefix)

    for dep in _get_libraries(path):
        if not dep.startswith(prefix):
            continue
        replace = RPATH + dep[prefix_len:]
        _replace_lib_name(path, dep, replace)

    # .dylib files should change their install_name too!
    install_name = _get_install_name(path)
    if install_name.startswith(prefix):
        new_install_name = RPATH + install_name[prefix_len:]
        _replace_install_name(path, new_install_name)


def set_rpaths(path, rpaths):
    """ Set the RPATHs for a mach-o file.
    """
    for rpath in rpaths:
        _run_install_name_tool('-add_rpath', rpath, path)


def _get_install_name(path):
    """ Use otool to find the install_name of a library.
    """
    for load in _iter_specific_load_commands(path, 'LC_ID_DYLIB'):
        name = load.get('name', ' ').split(' ', 1)[0]
        if name:
            return name
    return ''


def _get_libraries(path):
    """ Use otool to list the libraries of an executable.
    """
    libs = []
    for load in _iter_specific_load_commands(path, 'LC_LOAD_DYLIB'):
        name = load.get('name', ' ').split(' ', 1)[0]
        if name:
            libs.append(name)
    return libs


def _iter_load_commands(lines):
    """Iterate over load commands from `otool -l`
    """
    def _to_dict(cmd):
        return dict([c.strip().split(' ', 1) for c in cmd
                     if len(c) > 0 and ' ' in c])

    start = 1  # skip the first line
    for i, ln in enumerate(lines):
        if ln.startswith('Load command'):
            if start < i:
                yield _to_dict(lines[start+1:i])
            start = i
    yield _to_dict(lines[start+1:])


def _iter_specific_load_commands(path, cmd):
    """Pick out specific load commands
    """
    out = _run_otool(path)
    for load in _iter_load_commands(out):
        if load.get('cmd', '') == cmd:
            yield load


def _replace_install_name(path, new):
    """ Use install_name_tool to rename the install_name of a dylib
    """
    _run_install_name_tool('-id', new, path)


def _replace_lib_name(path, old, new):
    """ Use install_name_tool to rename dependencies
    """
    _run_install_name_tool('-change', old, new, path)


def _run_install_name_tool(*args):
    """ Use install_name_tool
    """
    cmdline = ['install_name_tool'] + list(args)
    p = subprocess.Popen(cmdline, stderr=subprocess.PIPE)
    try:
        _, err = p.communicate()
        err = bytes2str(err)
        if 'Mach-O dynamic shared library stub file' in err:
            return
        elif 'would duplicate path, file already has LC_RPATH for:' in err:
            return

        if p.returncode:
            print(err)
            msg = '"install_name_tool" failed. returncode = {}'
            raise RuntimeError(msg.format(p.returncode))
    except subprocess.TimeoutExpired:
        p.kill()


def _run_otool(path):
    """ Use otool -l to introspect an executable
    """
    cmdline = ['otool', '-l', path]
    p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    try:
        outs, _ = p.communicate()
        return bytes2str(outs).split('\n')
    except subprocess.TimeoutExpired:
        p.kill()
