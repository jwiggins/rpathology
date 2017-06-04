import sys

PY3K = sys.version_info > (3, 0)


def bytes2str(b):
    if PY3K:
        return b.decode('utf-8')
    else:
        return b
