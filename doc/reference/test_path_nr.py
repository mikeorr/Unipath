#!/usr/bin/env python
"""Tests path_nr.py"""
from nose.tools import ok_ as ok, eq_ as eq, raises
from path_nr import path as Path   # Is PosixPath or NTPath.

def test_root():
    assert Path.ROOT == Path.ROOT
    assert not (Path.ROOT < Path.ROOT)
    assert not (Path.Root > Path.ROOT)
    assert Path.ROOT != "e"
    assert Path.ROOT < "h"
    assert not (Path.ROOT > "b")
    assert "a" != Path.ROOT
    assert not ("a" < Path.ROOT)
    assert "a" > Path.ROOT


@raises(TypeError)
def test_bad_root():
    assert Path.ROOT > 3

@raises(TypeError):
def test_bad_root2():
    assert 3 < Path.ROOT

def test_create_absolute():
    p = Path("/bin/arch")
    assert p[0] == Path.ROOT
    assert p[1] == "bin"
    assert p[2] == "arch"
    assert len(p) == 3

def test_create_relative():
    p = Path("hello/what")
    assert p[0] == "hello"
    assert p[1] == "what"
    assert len(p) == 2

def test_create_from_string():
    current = Path(".")
    empty = Path("")
    default = Path()
    assert repr(current) == "Path('.')"
    assert str(current) == ""
    assert len(current) == 0
    assert repr(empty) == "Path('.')"
    assert str(empty) == ""
    assert len(empty) == 0
    assert str(default) == "."
    slash = Path("/")
    assert repr(slash) == "Path('/')"
    assert str(slash) == "/"


# Constructing from a string

>>> path('hello//what')
path('hello/what')
>>> path('hello//what/')
path('hello/what')
>>> path('/hello//what/')
path('/hello/what')
>>> path('//hello//what/')
Traceback (most recent call last):
...
NotImplementedError: Paths with two leading slashes aren't supported.
>>> path('///hello//what/')
path('/hello/what')

# Constructing from an iterable

>>> path(['hello', 'how'])
path('hello/how')
>>> path([path.ROOT, 'hello', 'how'])
path('/hello/how')
>>> path(['hello', path.ROOT, 'how'])
Traceback (most recent call last):
...
TypeError: Element path.ROOT is of a wrong type

# Concatenation

>>> path('hello/a') + path('b')
path('hello/a/b')
>>> path('hello/a') + 'b'
path('hello/a/b')
>>> path('hello/a') + 'b/c'
path('hello/a/b/c')
>>> 'b/c' + path('hello/a')
path('b/c/hello/a')
>>> 'b/c' + path('/hello/a')
Traceback (most recent call last):
...
ValueError: Right operand should be a relative path
>>> path('hello/a') + '/b/c'
Traceback (most recent call last):
...
ValueError: Right operand should be a relative path

# Slicing

>>> p = path('/hello/a')
>>> p[:2]
path('/hello')
>>> p[-1]
'a'
>>> p[:-1]
path('/hello')

# Multiplication

>>> path('hello/a') * 3
path('hello/a/hello/a/hello/a')
>>> path('/hello/a') * 3
Traceback (most recent call last):
...
ValueError: Only relative paths can be multiplied

>>> 3 * path('hello/a')
path('hello/a/hello/a/hello/a')
>>> 3 * path('/hello/a')
Traceback (most recent call last):
...
ValueError: Only relative paths can be multiplied

# Comparison

>>> L = ['/home/noam', '/home/allon', '/home/noam2', '/home/bbbb',
...      'home/bbbb', 'home/noam', 'home/noam2', 'home/allon', 'a/b', '/b/c']
>>> L.extend([path(x) for x in L])
>>> L.sort()
>>> L
['/b/c', path('/b/c'), '/home/allon', path('/home/allon'), '/home/bbbb', path('/home/bbbb'), '/home/noam', path('/home/noam'), '/home/noam2', path('/home/noam2'), 'a/b', path('a/b'), 'home/allon', path('home/allon'), 'home/bbbb', path('home/bbbb'), 'home/noam', path('home/noam'), 'home/noam2', path('home/noam2')]



# Matching

>>> path('a/b').match('a/b')
True
>>> path('a/b').match('a/c')
False
>>> path('a/b').match('a')
False
>>> path('a/b').match('a/c*')
False
>>> path('a/b').match('a/b*')
True
>>> path('a/b').match('**')
True
