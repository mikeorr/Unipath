"""Convenience functions.
"""
import sys

# Package imports.
from unipath import Path, FSPath

def dict2dir(dir, dic, mode="w"):
    dir = FSPath(dir)
    if not dir.exists():
        dir.mkdir()
    for filename, content in dic.iteritems():
        p = FSPath(dir, filename)
        if isinstance(content, dict):
            dict2dir(p, content)
            continue
        f = open(p, mode)
        f.write(content)
        f.close()

def dump_path(path, prefix="", tab="    ", file=None):
    if file is None:
        file = sys.stdout
    p = Path(path)
    if   p.islink():
        print >>file, "%s%s -> %s" % (prefix, p.name, p.read_link())
    elif p.isdir():
        print >>file, "%s%s:" % (prefix, p.name)
        for p2 in p.listdir():
            dump_path(p2, prefix+tab, tab, file)
    else:
        print >>file, "%s%s  (%d)" % (prefix, p.name, p.size())
