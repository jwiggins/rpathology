from platform import system

__sys_os = system().lower()
if __sys_os == 'linux':
    from .elf import (build_rpath, is_executable, get_missing_libraries,
                      get_rpaths, set_rpaths)
elif __sys_os == 'darwin':
    from .macho import (build_rpath, is_executable, get_missing_libraries,
                        get_rpaths, set_rpaths)
else:
    raise ImportError('This platform({}) is not supported!'.format(__sys_os))


# Keep flake8 happy without telling it to ignore everything
hushup_flake8 = [build_rpath, is_executable, get_missing_libraries, get_rpaths,
                 set_rpaths]
del hushup_flake8
