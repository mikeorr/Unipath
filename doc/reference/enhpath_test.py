#!/usr/bin/env python
"""A test suite for enhpath.py.
   Run using py.test from http://codespeak.net/py/current/doc/test.html
"""
import os, tempfile
import py.test
from enhpath import path

P1 = "aaa"
P2 = "aaa/bbb"
P3 = "aaa/bbb/ccc.txt"

def test_constructors():
    assert str(path(P1)) == P1
    assert str(path(P2)) == P2 
    assert str(path(P3)) == P3 
    assert str(path('')) == ''
    assert str(path())   == '' 
    assert str(path.cwd()) == os.getcwd()

def test_tempfile():
    path.tempfile()
    path.tempdir()
    assert isinstance(path.tempfileobject(), file)

def test_chdir():
    orig_dirs = path.pushed_dirs[:]
    origin = path(os.getcwd())
    tmp = path(tempfile.mkdtemp())
    try:
        # Chdir to tmp.
        tmp.chdir()
        assert os.getcwd() == tmp
        # Return to origin.
        origin.chdir()
        assert os.getcwd() == origin
        # Push to tmp.
        tmp.chdir(True)
        assert os.getcwd() == tmp
        assert path.pushed_dirs == orig_dirs + [origin]
        # Pop back to origin.
        path.popdir()
        assert os.getcwd() == origin
        assert path.pushed_dirs == orig_dirs
    finally:
        os.rmdir(tmp)
    
def test_repr():
    p = path(P1)
    assert repr(p) == "path(%r)" % P1
    path.repr_as_str = True
    assert repr(p) == "'%s'" % P1
    path.repr_as_str = False
    assert repr(p) == "path(%r)" % P1

def test_attributes():
    p = path(P3)
    assert p.parent == path('aaa/bbb')
    assert p.name == 'ccc.txt'
    assert p.base == 'ccc'
    assert p.ext == '.txt'

def test_operators():
    a = "aaa"
    b = "bbb"
    assert path(a) + path(b) == "aaabbb"
    assert path(a) / path(b) == os.path.join(a, b)

def test_normalization():
    cwd = os.getcwd()
    p = path(P3)
    ap = '/' + p
    assert p.abspath() == os.path.join(cwd, P3)
    assert ap.abspath() == '/' + P3
    assert not p.isabs()
    assert ap.isabs()
    assert p.abspath().relpath() == P3
    # Skipping .normcase(), .normpath() and .realpath()
    # Skipping .expand*(), .relpathto()

def test_derivation():
    p = path(P3)
    ap = '/' + p
    assert p.splitpath() == [
        path(''),  'aaa', 'bbb', 'ccc.txt']
    assert ap.splitpath() == [
        path('/'), 'aaa', 'bbb', 'ccc.txt']
    assert p.splitext() == (path('aaa/bbb/ccc'), '.txt')
    assert p.stripext() == path('aaa/bbb/ccc')
    assert path('aaa').joinpath('bbb', 'ccc.txt') == p
    assert p.ancestor(2) == path('aaa')
    assert p.ancestor(3) == path('')
    assert p.joinancestor(2, 'foo') == path('aaa/foo')
    assert p.joinancestor(3, 'foo') == path('foo')
    # Skipping .redeploy()

def test_relpathto():
    p = path('/home/joe/Mail')
    ancestor = path('/home/joe')
    bad_ancestor = path('BOGUS')
    assert p.relpathfrom(ancestor) == path('Mail')
    py.test.raises(ValueError, p.relpathfrom, bad_ancestor)

def test_listing():
    dir = path.tempdir()
    a = dir / 'a'
    b = dir / 'b'
    c = dir / 'c.txt'
    d = dir / 'd.asc'
    dev = path('/dev')
    try:
        a.mkdir()
        b.mkdir()
        c.write_text("foo\n")
        c.symlink(d)
        assert dir.listdir(names_only=True) == \
            ['a', 'b', 'c.txt', 'd.asc']
        assert dir.listdir('*.txt', names_only=True) == \
            ['c.txt']
        assert dir.listdir() == [a, b, c, d]
        assert dir.listdir(symlinks=False) == [a, b, c]
        assert dir.dirs() == [a, b]
        assert dir.dirs(symlinks=False) == [a, b]
        assert dir.files() == [c, d]
        assert dir.files(symlinks=False) == [c]
        assert dir.symlinks() == [d]
        assert dir.symlinks('*.txt') == []
        assert path('/dev/null') not in dev.files()
    finally:
        dir.delete_dammit()

def test_walk():
    dir = path.tempdir()
    a = dir / 'a'
    b = dir / 'b'
    a_files = [a / '1', a / '2', a / '3']
    b_files = [b / '4', b / '5', b / '6']
    try:
        a.mkdir()
        b.mkdir()
        for p in a_files + b_files:
            p.touch()
        assert dir.listdir() == [a, b]
        assert list(dir.walk()) == [a] + a_files + [b] + b_files 
        assert list(dir.walkdirs()) == [a, b]
        assert list(dir.walkfiles()) == a_files + b_files
    finally:
        dir.delete_dammit()

def test_walk2():
    """A more complicated walk test."""
    #dir = path('/tmp/X');  dir.mkdir()  #path.tempdir()
    dir = path.tempdir()
    a = dir / 'a'

    b = dir / 'b'
    a_files = [a / '1', a / '2', a / '3']
    b_files = [b / '4', b / '5', b / '6']
    subdir = a / 'subdir'
    subfiles = [subdir / 'A', subdir / 'B', subdir / 'C']
    target = subfiles[0]
    link = target.parent / 'link'
    try:
        for p in [a, b, subdir]:
            p.mkdir()
        for p in a_files + b_files + subfiles:
            p.touch()
        target.symlink(link)
        assert list(dir.walk()) == [a] + [subdir] + subfiles + [link] + \
            a_files + [b] + b_files
    finally:
        dir.delete_dammit()

def test_findpaths():
    #dir = path('/tmp/X');  dir.mkdir()  #path.tempdir()
    dir = path.tempdir()
    a = dir / 'a'
    b = dir / 'b'
    a_files = [a / '1', a / '2', a / '3']
    b_files = [b / '4', b / '5', b / '6']
    subdir = a / 'subdir'
    subfiles = [subdir / 'A', subdir / 'B', subdir / 'C']
    target = subfiles[0]
    link = target.parent / 'link'
    try:
        for p in [a, b, subdir]:
            p.mkdir()
        for p in a_files + b_files + subfiles:
            p.touch()
        target.symlink(link)
        assert list(dir.walk()) == [a] + [subdir] + subfiles + [link] + \
            a_files + [b] + b_files
        assert dir.findpaths_pretend() == ['find', dir]
        assert list(dir.findpaths()) == ([dir, a, subdir] + subfiles + 
            [link] + a_files +  [b] + b_files)
        assert list(b.findpaths()) == [b] + b_files
        dfp = dir.findpaths_pretend
        assert dfp(name='*') == ['find', dir, '-name', '*']
        assert dfp(name=('*.jpg', '*.png', '*.gif')) == \
            ['find', dir, '-lbrace', '-name', '*.jpg', '-or',
            '-name', '*.png', '-or', '-name', '*.gif', '-rbrace']
        assert dfp(maxdepth=1) == ['find', dir, '-maxdepth', '1']
        assert dfp(daystart=True) == ['find', dir, '-daystart']
        assert dfp(daystart=False) == ['find', dir]
        assert dfp(mtime=(-1, 1)) == \
            ['find', dir, '-mtime', '-1', '-mtime', '1']
        assert dfp('-type f') == ['find', dir, '-type', 'f']
        assert dfp('-type f') == dfp(['-type', 'f'])
    finally:
        dir.delete_dammit()

