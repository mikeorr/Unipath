UNIPATH
%%%%%%%

An object-oriented approach to file/directory operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Version:           0.2.0 (2008-05-17)
:Home page:         http://sluggo.scrapping.cc/python/unipath/
:Author:            Mike Orr <sluggoster@gmail.com>
:License:           Python (http://www.python.org/psf/license)
:Based on:          See HISTORY section below.

..
    To format this document as HTML:
    rst2html.py README.txt README.html

.. contents::

Introduction
============

Unipath is an object-oriented front end to the file/directory functions
scattered throughout several Python library modules.  It's based on Jason
Orendorff's *path.py* but does not adhere as strictly to the underlying
functions' syntax, in order to provide more user convenience and higher-level
functionality.  It comes with a test suite.

.. important::  Changes for Unipath 0.1.0 users

    ``Path`` has been renamed to ``AbstractPath``, and ``FSPath`` to ``Path``.
    ``FSPath`` remains as an alias for backward compatibility.
    ``Path.symlink()`` is gone; use ``Path.write_link()`` instead.  (Note that
    the argument order is the opposite.)  See CHANGES.txt for the complete list
    of changes.


The ``Path`` class encapsulates the file/directory operations in Python's
``os``, ``os.path``, and ``shutil`` modules.

Its superclass ``AbstractPath`` class encapsulates those operations which
aren't dependent on the filesystem.  This is mainly an academic distinction to
keep the code clean.  Since ``Path`` can do everything ``AbstractPath`` does,
most users just use ``Path``.

The API has been streamlined to focus on what the application developer wants
to do rather than on the lowest-level operations; e.g., ``.mkdir()`` succeeds
silently if the directory already exists, and ``.rmtree()`` doesn't barf if the
target is a file or doesn't exist.  This allows the developer to write simple
calls that "just work" rather than entire if-stanzas to handle low-level
details s/he doesn't care about.  This makes applications more self-documenting
and less cluttered.

Convenience methods: 

  * ``.read_file`` and ``.write_file`` encapsulate the open/read/close pattern.
  * ``.needs_update(others)`` tells whether the path needs updating; i.e., 
    if it doesn't exist or is older than any of the other paths.
  * ``.ancestor(N)`` returns the Nth parent directory, useful for joining paths.
  * ``.child(\*components)`` is a "safe" version of join.
  * ``.split_root()`` handles slash/drive/UNC absolute paths in a uniform way.

- Optional high-level functions in the ``unipath.tools`` module.

- For Python >= 2.4

- Path objects are immutable so can be used as dictionary keys.

Sample usage for pathname manipulation::

    >>> from unipath import Path
    >>> p = Path("/usr/lib/python2.5/gopherlib.py")
    >>> p.parent
    Path("/usr/lib/python2.5")
    >>> p.name
    Path("gopherlib.py")
    >>> p.ext
    '.py'
    >>> p.stem
    Path('gopherlib')
    >>> q = Path(p.parent, p.stem + p.ext)
    >>> q
    Path('/usr/lib/python2.5/gopherlib.py')
    >>> q == p
    True

Sample usage for filesystem access::

    >>> import tempfile
    >>> from unipath import Path
    >>> d = Path(tempfile.mkdtemp())
    >>> d.isdir()
    True
    >>> p = Path(d, "sample.txt")
    >>> p.exists()
    False
    >>> p.write_file("The king is a fink!")
    >>> p.exists()
    True
    >>> print p.read_file()
    The king is a fink!
    >>> d.rmtree()
    >>> p.exists()
    False

The name "Unipath" is short for "universal path", as it grew out of a
discussion on python-dev about the ideal path API for Python.

Unipath's API is mostly stable but there's no guarantee it won't change in
future versions.


Installation and testing
========================
If you have EasyInstall, run "easy_install unipath".  Otherwise unpack the
source and run "python setup.py install" in the top-level directory.
You can also copy the "unipath" directory to somewhere on your Python
path.

To test the library you'll need the Nose package.  cd to the top-level
directory and run "python unipath/test.py".


Path and AbstractPath objects
=============================

Constructor
-----------
``Path`` (and ``AbstractPath``) objects can be created from a string path, or
from several string arguments which are joined together a la ``os.path.join``.
Each argument can be a string, an ``(Abstract)Path`` instance, an int or long,
or a list/tuple of strings to be joined::

    p = Path("foo/bar.py")       # A relative path
    p = Path("foo", "bar.py")    # Same as previous
    p = Path(["foo", "bar.py"])  # Same as previous
    p = Path("/foo", "bar", "baz.py")       # An absolute path: /foo/bar/baz.py
    p = Path("/foo", Path("bar/baz.py"))    # Same as previous
    p = Path("/foo", ["", "bar", "baz.py"]) # Embedded Path.components() result
    p = Path("record", 123)      # Same as Path("record/123")

    p = Path("")     # An empty path
    p = Path()       # Same as Path(os.curdir)

To get the actual current directory, use ``Path.cwd()``.  (This doesn't work
with ``AbstractPath``, of course.

Adding two paths results in a concatenated path.  The other string methods
return strings, so you'll have to wrap them in ``Path`` to make them paths
again. A future version will probably override these methods to return paths.
Multiplying a path returns a string, as if you'd ever want to do that.

Normalization
-------------
The new path is normalized to clean up redundant ".." and "." in the
middle, double slashes, wrong-direction slashes, etc.  On
case-insensitive filesystems it also converts uppercase to lowercase.
This is all done via ``os.path.normpath()``.  Here are some examples
of normalizations::

    a//b  => a/b
    a/../b => b
    a/./b => a/b
    
    a/b => a\\b            # On NT.
    a\\b.JPG => a\\b.jpg   # On NT.

If the actual filesystem path contains symbolic links, normalizing ".." goes to
the parent of the symbolic link rather than to the parent of the linked-to
file.  For this reason, and because there may be other cases where normalizing
produces the wrong path, you can disable automatic normalization by setting the
``.auto_norm`` class attribute to false.  I'm not sure whether Unipath should
normalize by default, so if you care one way or the other you should explicitly
set it at the beginning of your application.  You can override the auto_norm
setting by passing "norm=True" or "norm=False" as a keyword argument to the
constructor.  You can also call ``.norm()`` anytime to manually normalize the
path.


Properties
----------
Path objects have the following properties:

.parent
    The path without the final component.
.name
    The final component only.
.ext
    The last part of the final component beginning with a dot (e.g., ".gz"), or
    "" if there is no dot.  This is also known as the extension.
.stem
    The final component without the extension.

Examples are given in the first sample usage above.


Methods
-------
Path objects have the following methods:

.ancestor(N)
    Same as specifying ``.parent`` N times.

.child(\*components)
    Join paths in a safe manner.  The child components may not contain a path
    separator or be curdir or pardir ("." or ".." on Posix).  This is to
    prevent untrusted arguments from creating a path above the original path's
    directory.  

.components()
    Return a list of directory components as strings.  The first component will
    be the root ("/" on Posix, a Windows drive root, or a UNC share) if the
    path is absolute, or "" if it's relative.  Calling ``Path(components)``,
    ``Path(*components)``, or ``os.path.join(*components)`` will recreate the
    original path.

.expand()
    Same as ``p.expand_user().expand_vars().norm()``.  Usually this is all
    you need to fix up a path read from a config file.

.expand_user()
    Interpolate "~" and "~user" if the platform allows, and return a new path.

.expand_vars()
    Interpolate environment variables like "$BACKUPS" if the platform allows,
    and return a new path.

.isabsolute()
    Is the path absolute?

.norm()
    See Normalization above.  Same as ``os.path.normpath``.

.norm_case()
    On case-insensitive platforms (Windows) convert the path to lower case.
    On case-sensitive platforms (Unix) leave the path as is.  This also turns
    forward slashes to backslashes on Windows.

.split_root()
    Split this path at the root and return a tuple of two paths: the root and
    the rest of the path.  The root is the same as the first subscript of the
    ``.components()`` result.  Calling ``Path(root, rest)`` or
    ``os.path.join(root, rest)`` will produce the original path.

Examples::
    
    Path("foo/bar.py").components() => 
        [Path(""), Path("foo"), Path("bar.py")]
    Path("foo/bar.py").split_root() => 
        (Path(""), Path("foo/bar.py"))

    Path("/foo/bar.py").components() => 
        [Path("/"), Path("foo"), Path("bar.py")]
    Path("/foo/bar.py").split_root() => 
        (Path("/"), Path("foo/bar.py"))

    Path("C:\\foo\\bar.py").components() => 
        ["Path("C:\\"), Path("foo"), Path("bar.py")]
    Path("C:\\foo\\bar.py").split_root() => 
        ("Path("C:\\"), Path("foo\\bar.py"))

    Path("\\\\UNC_SHARE\\foo\\bar.py").components() =>
        [Path("\\\\UNC_SHARE"), Path("foo"), Path("bar.py")]
    Path("\\\\UNC_SHARE\\foo\\bar.py").split_root() =>
        (Path("\\\\UNC_SHARE"), Path("foo\\bar.py"))

    Path("~/bin").expand_user() => Path("/home/guido/bin")
    Path("~timbot/bin").expand_user() => Path("/home/timbot/bin")
    Path("$HOME/bin").expand_vars() => Path("/home/guido/bin")
    Path("~//$BACKUPS").expand() => Path("/home/guido/Backups")

    Path("dir").child("subdir", "file") => Path("dir/subdir/file")

    Path("/foo").isabsolute() => True
    Path("foo").isabsolute() => False

Note: a Windows drive-relative path like "C:foo" is considered absolute by
``.components()``, ``.isabsolute()``, and ``.split_root()``, even though 
Python's ``ntpath.isabs()`` would return false.

Path objects only
=================

Note on arguments
-----------------
All arguments that take paths can also take strings.

Current directory
-----------------

Path.cwd()
    Return the actual current directory; e.g., Path("/tmp/my_temp_dir").
    This is a class method.

.chdir()
    Make self the current directory.

Calculating paths
-----------------
.resolve()
    Return the equivalent path without any symbolic links.  This normalizes
    the path as a side effect.

.absolute()
    Return the absolute equivalent of self.  If the path is relative, this
    prefixes the current directory; i.e., ``FSPath(FSPath.cwd(), p)``.

.relative()
    Return an equivalent path relative to the current directory if possible.
    This may return a path prefixed with many "../..".  If the path is on a
    different drive, this returns the original path unchanged.

.rel_path_to(other)
    Return a path from self to other.  In other words, return a path for
    'other' relative to self.

Listing directories
-------------------
*These methods are experimental and subject to change.*

.listdir(pattern=None, filter=ALL, names_only=False)
    Return the filenames in this directory.

    'pattern' may be a glob expression like "\*.py".

    'filter' may be a function that takes a ``FSPath`` and returns true if it
    should be included in the results.  The following standard filters are
    defined in the ``unipath`` module: 
    
        - ``DIRS``: directories only
        - ``FILES``: files only
        - ``LINKS``: symbolic links only
        - ``FILES_NO_LINKS``: files that aren't symbolic links
        - ``DIRS_NO_LINKS``: directories that aren't symbolic links
        - ``DEAD_LINKS``: symbolic links that point to nonexistent files

    This method normally returns FSPaths prefixed with 'self'.  If
    'names_only' is true, it returns the raw filenames as strings without a
    directory prefix (same as ``os.listdir``).

    If both 'pattern' and 'filter' are specified, only paths that pass both are
    included.  'filter' must not be specified if 'names_only' is true.

    Paths are returned in sorted order.
    

.walk(pattern=None, filter=None, top_down=True)

    Yield ``FSPath`` objects for all files and directories under self,
    recursing subdirectories.  Paths are yielded in sorted order.

    'pattern' and 'filter' are the same as for ``.listdir()``.

    If 'top_down' is true (default), yield directories before yielding
    the items in them.  If false, yield the items first.


File attributes and permissions
-------------------------------
.atime()
    Return the path's last access time.

.ctime()
    Return the path's ctime.  On Unix this returns the time the path's
    permissions and ownership were last modified.  On Windows it's the path
    creation time.

.exists()
    Does the path exist?  For symbolic links, True if the linked-to file
    exists.  On some platforms this returns False if Python does not have
    permission to stat the file, even if it exists.

.isdir()
    Is the path a directory?  Follows symbolic links.

.isfile()
    Is the path a file?  Follows symbolic links.

.islink()
    Is the path a symbolic link?

.ismount()
    Is the path a mount point?  Returns true if self's parent is on a
    different device than self, or if self and its parent are the same
    directory.

.lexists()
    Same as ``.exists()`` but don't follow a final symbolic link.

.lstat()
    Same as ``.stat()`` but do not follow a final symbolic link.

.size()
    Return the file size in bytes.

.stat()
    Return a stat object to test file size, type, permissions, etc.
    See ``os.stat()`` for details.

.statvfs()
    Return a ``StatVFS`` object.  This method exists only if the platform
    supports it.  See ``os.statvfs()`` for details.


Modifying paths
---------------

Creating/renaming/removing
++++++++++++++++++++++++++

.chmod(mode)
    Change the path's permissions.  'mode' is octal; e.g., 0777.

.chown(uid, gid)
    Change the path's ownership to the numeric uid and gid specified.
    Pass -1 if you don't want one of the IDs changed.

.mkdir(parents=False)
    Create the directory, or succeed silently if it already exists.  If
    'parents' is true, create any necessary ancestor directories.

.remove()
    Delete the file.  Raises OSError if it's a directory.

.rename(dst, parents=False)
    Rename self to 'dst' atomically.  See ``os.rename()`` for additional
    details.  If 'parents' is True, create any intermediate destination
    directories necessary, and delete as many empty leaf source directories as
    possible.

.rmdir(parents=False)
    Remove the directory, or succeed silently if it's already gone.  If 
    'parents' is true, also remove as many empty ancestor directories as
    possible.

.set_times(mtime=None, atime=None)
    Set the path's modification and access times.  If 'mtime' is None, use
    the current time.  If 'atime' is None or not specified, use the same time
    as 'mtime'.  To set the times based on another file, see ``.copy_stat()``.

Symbolic and hard links
+++++++++++++++++++++++

.hardlink(src)
    Create a hard link at 'src' pointing to self.

.write_link(target)
    Create a symbolic link at self pointing to 'target'.  The link will contain
    the exact string value of 'target' without checking whether that path exists
    or is a even a valid path for the filesystem.

.make_relative_link_to(dst)
    Make a relative symbolic link from self to dst.  Same as
    ``self.write_link(self.rel_path_to(dst))``.  (New in Unipath 0.2.0.)

.read_link()
    Return the path that this symbolic link points to.

High-level operations
---------------------
.copy(dst, times=False, perms=False)
    Copy the file to a destination.  'times' and 'perms' are same as for
    ``.copy_stat()``.

.copy_stat(dst, times=True, perms=True)
    Copy the access/modification times and/or the permission bits from this
    path to another path.

.copy_tree(dst, preserve_symlinks=False, times=False, perms=False)
    Recursively copy a directory tree to 'dst'.  'dst' must not exist; it will
    be created along with any missing ancestors.  If 'symlinks' is true,
    symbolic links will be recreated with the same path (absolute or relative);
    otherwise the links will be followed.  'times' and 'perms' are same as
    ``.copy_stat()``.  *This method is not implemented yet.*

.move(dst)
    Recursively move a file or directory to another location.  This uses
    .rename() if possible.

.needs_update(other_paths)
    Return True if self is missing or is older than any other path.
    'other_paths' can be a ``(FS)Path``, a string path, or a list/tuple
    of these.  Recurses through subdirectories but compares only files.

.read_file(mode="r")
    Return the file's content as a ``str`` string.  This encapsulates the
    open/read/close.  'mode' is the same as in Python's ``open()`` function.

.rmtree(parents=False)
    Recursively remove this path, no matter whether it's a file or a 
    directory.  Succeed silently if the path doesn't exist.  If 'parents' is
    true, also try to remove as many empty ancestor directories as possible.

.write_file(content, mode="w")
    Replace the file's content, creating the file if
    necessary.  'mode' is the same as in Python's ``open()`` function.
    'content' is a ``str`` string.  You'll have to encode Unicode strings
    before calling this.

Tools
=====
The following functions are in the ``unipath.tools`` module.

dict2dir
--------
dict2dir(dir, dic, mode="w")  =>  None
    
    Create a directory that matches the dict spec.  String values are turned
    into files named after the key.  Dict values are turned into 
    subdirectories.  'mode' specifies the mode for files.  'dir' can be an
    ``[FS]Path`` or a string path.

dump_path(path, prefix="", tab="    ", file=None)  =>  None

    Display an ASCII tree of the path.  Files are displayed as 
    "filename (size)".  Directories have ":" at the end of the line and
    indentation below, like Python syntax blocks.  Symbolic links are
    shown as "link -> target".  'prefix' is a string prefixed to every
    line, normally to controll indentation.  'tab' is the indentation
    added for each directory level.  'file' specifies an output file object,
    or ``None`` for ``sys.stdout``.

    A future version of Unipath will have a command-line program to 
    dump a path.


Non-native paths
================

If you want to make Windows-style paths on Unix or vice-versa, you can 
subclass ``AbstractPath`` and set the ``pathlib`` class attribute to one of
Python's OS-specific path modules (``posixpath`` or ``ntpath``) or a 
third-party equivalent.  To convert from one syntax to another, pass the path
object to the other constructor.

This is not practical with ``Path`` because the OS will reject or misinterpret
non-native paths.

History
=======
2004-03-07
    Released as path.py by Jason Orendorff <jason@jorendorff.com>.
    That version is a subclass of unicode and combines methods from
    os.path, os, and shutil, and includes globbing features.
    Other contributors are listed in the source.

    - http://www.jorendorff.com/articles/python/path
    
2005-07
    Modified by Reinhold Birkenfeld in preparation for a Python PEP.
    Convert all filesystem-accessing properties to methods, rename stuff, and
    use self.__class__ instead of hardwired constructor to aid subclassing.
    Source was in Python CVS in the "sandbox" section but I can't find it in 
    the current Subversion repository; was it deleted?  What's the incantation
    to bring it back?

2006-01
    Modified by Björn Lindqvist <bjourne@gmail.com> for PEP 355.
    Replace .joinpath() with a multi-argument constructor.

    - overview:  http://www.python.org/dev/peps/pep-0355/
    - code:  http://wiki.python.org/moin/PathModule
    
2006
    Influenced by Noam Raphael's alternative path module.  This subclasses
    tuple rather than unicode, representing a tuple of directory components a
    la ``tuple(os.path.splitall("a/b"))``. The discussion covers several design
    decisions and open issues.

    - overview:  http://wiki.python.org/moin/AlternativePathClass
    - code:  http://wiki.python.org/moin/AlternativePathModule
    - discussion:  http://wiki.python.org/moin/AlternativePathDiscussion

2007-01
    Renamed unipath and modified by Mike Orr <sluggoster@gmail.com>.
    Move filesystem operations into a subclass FSPath.  Add and rename methods
    and properties.  Influenced by these mailing-list threads:

    - @@MO coming soon

2008-05
    Released version 0.2.0.  Renamed ``Path`` to ``AbstractPath``, and
    ``FSPath`` to ``Path``.

Comparision with os/os.path/shutil and path.py
==============================================
::

    p = any path, f =  file, d = directory, l = link
    fsp, fsf, fsd, fsl = filesystem path (i.e., ``Path`` only)
    - = not implemented

Functions are listed in the same order as the Python Library Reference, version
2.5.  (Sorry the table is badly formatted.)

::

    os/os.path/shutil      path.py        Unipath           Notes
    =================      ============== ==========        =======
    os.path.abspath(p)     p.abspath()    p.absolute()     Return absolute path.
    os.path.basename(p)    p.name         p.name
    os.path.commonprefix(p)  -            -                Common prefix. [1]_
    os.path.dirname(p)     p.parent       p.parent         All except the last component.
    os.path.exists(p)      p.exists()     fsp.exists()     Does the path exist?
    os.path.lexists(p)     p.lexists()    fsp.lexists()    Does the symbolic link exist?
    os.path.expanduser(p)  p.expanduser() p.expand_user()  Expand "~" and "~user" prefix.
    os.path.expandvars(p)  p.expandvars() p.expand_vars()  Expand "$VAR" environment variables.
    os.path.getatime(p)    p.atime        fsp.atime()      Last access time.
    os.path.getmtime(p)    p.mtime        fsp.mtime()      Last modify time.
    os.path.getctime(p)    p.ctime        fsp.ctime()      Platform-specific "ctime".
    os.path.getsize(p)     p.size         fsp.size()       File size.
    os.path.isabs(p)       p.isabs()      p.isabsolute     Is path absolute?
    os.path.isfile(p)      p.isfile()     fsp.isfile()     Is a file?
    os.path.isdir(p)       p.isdir()      fsp.isdir()      Is a directory?
    os.path.islink(p)      p.islink()     fsp.islink()     Is a symbolic link?
    os.path.ismount(p)     p.ismount()    fsp.ismount()    Is a mount point?
    os.path.join(p, "Q/R") p.joinpath("Q/R")  [FS]Path(p, "Q/R")  Join paths.
                                              -or-
                                              p.child("Q", "R")
    os.path.normcase(p)    p.normcase()    p.norm_case()   Normalize case.
    os.path.normpath(p)    p.normpath()    p.norm()        Normalize path.
    os.path.realpath(p)    p.realpath()    fsp.real_path() Real path without symbolic links.
    os.path.samefile(p, q) p.samefile(q)   fsp.same_file(q)  True if both paths point to the same filesystem item.
    os.path.sameopenfile(d1, d2)  -          -               [Not a path operation.]
    os.path.samestat(st1, st2)    -          -               [Not a path operation.]
    os.path.split(p)       p.splitpath()   (p.parent, p.name) Split path at basename.
    os.path.splitdrive(p)  p.splitdrive()   -                 [2]_
    os.path.splitext(p)    p.splitext()     -                 [2]_
    os.path.splitunc(p)    p.splitunc()     -                 [2]_
    os.path.walk(p, func, args)  -          -                 [3]_

    os.access(p, const)    p.access(const)  -                 [4]_
    os.chdir(d)            -                fsd.chdir()       Change current directory.
    os.fchdir(fd)          -                -                 [Not a path operation.]
    os.getcwd()           path.getcwd()     FSPath.cwd()      Get current directory.
    os.chroot(d)          d.chroot()        -                 [5]_
    os.chmod(p, 0644)     p.chmod(0644)     fsp.chmod(0644)     Change mode (permission bits).
    os.chown(p, uid, gid) p.chown(uid, gid) fsp.chown(uid, gid) Change ownership.
    os.lchown(p, uid, gid) -                -                 [6]_
    os.link(src, dst)     p.link(dst)       fsp.hardlink(dst)   Make hard link.
    os.listdir(d)         -                 fsd.listdir(names_only=True)  List directory; return base filenames.
    os.lstat(p)           p.lstat()         fsp.lstat()         Like stat but don't follow symbolic link.
    os.mkfifo(p, 0666)    -                 -                 [Not enough of a path operation.]
    os.mknod(p, ...)      -                 -                 [Not enough of a path operation.]
    os.major(device)      -                 -                 [Not a path operation.]
    os.minor(device)      -                 -                 [Not a path operation.]
    os.makedev(...)       -                 -                 [Not a path operation.]
    os.mkdir(d, 0777)     d.mkdir(0777)     fsd.mkdir(mode=0777)     Create directory.
    os.makedirs(d, 0777)  d.makedirs(0777)  fsd.mkdir(True, 0777)    Create a directory and necessary parent directories.
    os.pathconf(p, name)  p.pathconf(name)  -                  Return Posix path attribute.  (What the hell is this?)
    os.readlink(l)        l.readlink()      fsl.read_link()      Return the path a symbolic link points to.
    os.remove(f)          f.remove()        fsf.remove()       Delete file.
    os.removedirs(d)      d.removedirs()    fsd.rmdir(True)    Remove empty directory and all its empty ancestors.
    os.rename(src, dst)   p.rename(dst)     fsp.rename(dst)      Rename a file or directory atomically (must be on same device).
    os.renames(src, dst)  p.renames(dst)    fsp.rename(dst, True) Combines os.rename, os.makedirs, and os.removedirs.
    os.rmdir(d)           d.rmdir()         fsd.rmdir()        Delete empty directory.
    os.stat(p)            p.stat()          fsp.stat()         Return a "stat" object.
    os.statvfs(p)         p.statvfs()       fsp.statvfs()      Return a "statvfs" object.
    os.symlink(src, dst)  p.symlink(dst)    fsp.write_link(link_text)   Create a symbolic link. 
                                            ("write_link" argument order is opposite from Python's!)
    os.tempnam(...)       -                 -                  [7]_
    os.unlink(f)          f.unlink()        -                  Same as .remove().
    os.utime(p, times)    p.utime(times)    fsp.set_times(mtime, atime)  Set access/modification times.
    os.walk(...)          -                 -                  [3]_

    shutil.copyfile(src, dst)  f.copyfile(dst) fsf.copy(dst, ...)  Copy file.  Unipath method is more than copyfile but less than copy2.
    shutil.copyfileobj(...)   -             -                  [Not a path operation.]
    shutil.copymode(src, dst) p.copymode(dst)  fsp.copy_stat(dst, ...)  Copy permission bits only.
    shutil.copystat(src, dst) p.copystat(dst)  fsp.copy_stat(dst, ...)  Copy stat bits.
    shutil.copy(src, dst)  f.copy(dst)      -                  High-level copy a la Unix "cp".
    shutil.copy2(src, dst) f.copy2(dst)     -                  High-level copy a la Unix "cp -p".
    shutil.copytree(...)  d.copytree(...)   fsp.copy_tree(...)   Copy directory tree.  (Not implemented in Unipath 0.1.0.)
    shutil.rmtree(...)    d.rmtree(...)     fsp.rmtree(...)    Recursively delete directory tree.  (Unipath has enhancements.)
    shutil.move(src, dst) p.move(dst)       fsp.move(dst)      Recursively move a file or directory, using os.rename() if possible.

    A + B                 A + B             A+B                Concatenate paths.
    os.path.join(A, B)    A / B             [FS]Path(A, B)     Join paths.
                                            -or-
                                            p.child(B)
    -                     p.expand()        p.expand()         Combines expanduser, expandvars, normpath.
    os.path.dirname(p)    p.parent          p.parent           Path without final component.
    os.path.basename(p)   p.name            p.name             Final component only.
    [8]_                  p.namebase        p.stem             Final component without extension.
    [9]_                  p.ext             p.ext              Extension only.
    os.path.splitdrive(p)[0] p.drive        -                  [2]_
    -                     p.stripext()      -                  Strip final extension.
    -                     p.uncshare        -                  [2]_
    -                     p.splitall()      p.components()     List of path components.  (Unipath has special first element.)
    -                     p.relpath()       fsp.relative()       Relative path to current directory.
    -                     p.relpathto(dst)  fsp.rel_path_to(dst) Relative path to 'dst'.
    -                     d.listdir()       fsd.listdir()        List directory, return paths.
    -                     d.files()         fsd.listdir(filter=FILES)  List files in directory, return paths.
    -                     d.dirs()          fsd.listdir(filter=DIRS)   List subdirectories, return paths.
    -                     d.walk(...)       fsd.walk(...)        Recursively yield files and directories.
    -                     d.walkfiles(...)  fsd.walk(filter=FILES)  Recursively yield files.
    -                     d.walkdirs(...)   fsd.walk(filter=DIRS)  Recursively yield directories.
    -                     p.fnmatch(pattern)  -                 True if self.name matches glob pattern.
    -                     p.glob(pattern)   -                   Advanced globbing.
    -                     f.open(mode)      -                   Return open file object.
    -                     f.bytes()         fsf.read_file("rb")   Return file contents in binary mode.
    -                     f.write_bytes()   fsf.write_file(content, "wb")  Replace file contents in binary mode.
    -                     f.text(...)       fsf.read_file()       Return file content.  (Encoding args not implemented yet.)
    -                     f.write_text(...) fsf.write_file(content)  Replace file content.  (Not all Orendorff args supported.)
    -                     f.lines(...)      -                   Return list of lines in file.
    -                     f.write_lines(...)  -                 Write list of lines to file.
    -                     f.read_md5()      -                   Calculate MD5 hash of file.
    -                     p.owner           -                   Advanded "get owner" operation.
    -                     p.readlinkabs()   -                   Return the path this symlink points to, converting to absolute path.
    -                     p.startfile()     -                   What the hell is this?

    -                     -                 p.split_root()      Unified "split root" method.
    -                     -                 p.ancestor(N)       Same as specifying .parent N times.
    -                     -                 p.child(...)        "Safe" way to join paths.
    -                     -                 fsp.needs_update(...) True if self is missing or older than any of the other paths.


.. [1] The Python method is too dumb; it can end a prefix in the middle of a
.. [2] Closest equivalent is ``p.split_root()`` for approximate equivalent.
.. [3] More convenient alternatives exist.
.. [4] Inconvenient constants; not used enough to port.
.. [5] Chroot is more of an OS operation than a path operation.  Plus it's 
   dangerous.
.. [6] Ownership of symbolic link doesn't matter because the OS never 
   consults its permission bits.
.. [7]_ ``os.tempnam`` is insecure; use ``os.tmpfile`` or ``tempfile`` module
   instead.
.. [8]_ ``os.path.splitext(os.path.split(p))[0]``
.. [9]_ ``os.path.splitext(os.path.split(p))[1]``
.. [10]_ Closest equivalent is ``p.split_root()[0]``.


Design decisions / open issues
==============================
(Sorry this is so badly organized.)

The original impetus for Unipath was to get object-oriented paths into the
Python standard library.  All the previous path classes were rejected as
too large and monolithic, especially for mixing pathname manipulations and
filesystem methods in the same class.  Upon reflection, it's mainly the
pathname operations that need to be OO-ified because they are often nested in
expressions.  There's a small difference between ``p.mkdir()`` and
``os.mkdir(p)``, but there's a huge difference between
``os.path.join(os.path.dirname(os.path.dirname("/A/B/C"))), "app2/lib")`` and
``Path("/A/B/C").parent.parent.child("app2", "lib")``: the former is flat-out
unreadable.  So I have kept ``Path`` to a conservative API that hopefully most
Pythoneers can agree on.  I allowed myself more freedom with ``FSPath``
because it's unclear that a class with filesystem methods would ever be
accepted into the stdlib anyway, and I needed an API I'd want to use in my own
programs.  (``Path`` was renamed to ``AbstractPath`` in Unipath 0.2.0, and
``FSPath`` to ``Path``.  This section uses the older vocabulary.)

Another important point is that properties may not access the filesystem.
Only methods may access the filesystem.  So ``p.parent`` is a property, but
``p.mtime()`` is a method.  This required turning some of Orendorff's 
properties into methods.

The actual ``FSPath`` class ended up closer to Orendorff's original than
I had intended, because several of the planned innovations (from python-3000
suggestions, Raphael's alternative path class, and my own mind) turned to be
not necessarily superior in actual programs, whereas Orendorff's methods have
proven themselves reliable in production systems for three years now, so I
deferred to them when in doubt.  

The biggest such move was making ``FSPath`` a
subclass of ``Path``.  Originally I had tried to make them unrelated classes
(``FSPath`` containing a ``Path``), but this became unworkable in the
implementation due to the constant need to call both types of methods. 
(Say you have an FSPath directory and you need to join a
filename to it and then delete the file; do you really want to convert from
FSPath to Path and back again?  Do you *really* want to write
"FSPath(Path(my_fspath.path, 'foo'))"?)  So one class is better than two, even
if the BDFL disapproves.  I opted for the best of both worlds via inheritance,
so those who want one class can pretend it is, and those who want two classes
can get a warm fuzzy feeling that they're defined separately. (They can even
ignore ``FSPath`` and use ``Path`` with ``os.*`` functions if they prefer.)
If ``Path`` is someday accepted into the standard libary, ``FSPath`` will
become a subclass of that.  And others can subclass ``FSPath`` or write an
alternative if they don't like my API.

I also intended to put all non-trivial code into generic functions that
third-party path libraries could call.  But that also became unworkable due to
the tight integration that naturally occurs between the methods, one calling
another.  What's really needed now is for ``FSPath`` to get into the real world
so we can see which generic code actually is valuable, and then those can be
factored out later.

``.stem`` is called stem because "namebase" can be confused with
``os.path.basename()``, "name_without_ext" is too wordy, and "name_no_ext" is
looks like bad English.

All method names have underscores between words except those starting with
"is", "mk", "rm", and "stat".  The "is" methods are so highly used that
deviating from the ``os.path``/Orendorff spelling would trip up a lot of
programmers, including me.  "mk" and "rm" I just like.  (Be glad I didn't
rename ``.copy_tree`` to "cptree" to match ``.rmtree``.) (or ".drive" and
".unc" properties) are not needed.  They may be added if they prove necessary,
but then how do you get "everything except the drive" or "everything except the
UNC prefix".  I also had to move the slash following the UNC prefix to the
prefix itself, to maintain the rule that everything after the first component
is a relative path.

I tried making a smart stat object so that one could do "p.stat().size" and
"p.stat().isdir".  This was one of the proposals for Raphael's class, to get
rid of a bunch of top-level methods and obviate the need for a set of "l"
methods covering the "stat" and "lstat" operations.  I also made a phony stat
object if the path didn't exist, to hang the ".exists" attribute off.  But I
was so used to typing ``p.isdir()`` etc from Orendorff that I couldn't adjust.
And Python has only one "l" function anyway, ``os.path.lexists()``.  *And* I
didn't want to write the stat object in C, meaning every stat would incur
Python overhead to convert the result attributes.  So in the end I decided to
keep the methods shadowing the ``os.path`` convenience functions, remove the
"get" prefix from the "get" methods ("getmtime"), and let ``.stat`` and
``.statvfs`` return the Python default object.  I'm still tempted to make
``.stat()`` and ``.statvfs`` return ``None`` if the path doesn't exist (rather
than raising ``OSError``), but I'm not sure that's necessarily *better* so I
held off on that.  Presumably one wouldn't use ``.stat()`` that much anyway
since the other methods are more convenient.

``.components()`` comes from Raphael's class, the concept of treating paths as
a list of components, with the first component being the filesystem root (for
an absolute path).  This required unifying Posix and Windows roots into a
common definition.  ``.split_root()`` handles drive paths and UNC paths, so
"splitdrive" and "splitunc" (or ".drive" and ".unc" properties) were deemed
unnecessary.  They may be added later if needed.  One problem with ".drive" and
".unc" properties is how to specify "everything except the drive" and
"everything except the UNC prefix", which are needed to recreate the path or
derive a similar path.  The slash after the UNC prefix was also moved to the
prefix, to maintain the rule that all components after the first make a
relative path.

"Components" turned out to be a useful way to convert paths from one platform
to another, which was one of Talin's requests.  However, what Talin really
wanted was to put Posix paths in a config file and have them translate to the
native platform.  Since ``.norm()`` and ``.norm_case()`` already do this on
Windows, it's questionable how much cross-platform support is really necessary.
Especially since ``macpath`` is obsolete now that Mac OS X uses Posix, and Mac
OS 9 is about to be dropped from Python.  So the multi-platform code is
probational.

Joining paths is done via the constructor, which takes multiple positional
arguments.  This was deemed as better than Orendorff's ".joinpath" method for
reasons I'm not sure of.  

``.child()`` was requested by Glyph, to create safe subpaths that can never
reach outside their parent directory even if based on untrusted user strings.
It's also sneaky way to do "joinpath" when you're really prefer to use a method
rather than the costructor, as long as each component has to be passed as a
separate argument.

Orendorff has ".listdir", ".dirs", and ".files" methods (non-recursive), and
".walk", ".walkdirs", and "walkfiles" (recursive).  Raphael has one ".glob"
method to rule them all.  I went back and forth on this several times and
finally settled on ``.listdir`` (non-recursive) and ``.walk`` (recursive), with
a 'filter' argument to return only files or directories.  Neither Orendorff nor
Raphael nor ``os.walk`` handle symlinks adequately in my opinion: sometimes you
want to exclude symlinks and then list them separately.  ``.listdir`` has a
'names_only' option to make it return just the filenames like ``os.listdir``,
because sometimes that's what you need, and there's no reason to create paths
you're just going to unpack again anyway.  ``.listdir`` and ``.walk`` are
separate methods because implementing them as one is complicated -- they have
so many contingencies.  ``.listdir()`` and ``.listdir(names_only=True)`` are
the same method because I couldn't come up with a better name for the former.
I dropped the name "glob" because it's meaningless to non-Unix users.

``.absolute``, ``.relative``, and ``.resolve`` are hopefully better named than
Orendorff's "abspath", "relpath", and "realpath", which were taken directly
from ``os.path``.  ``.hardlink`` is so-named because it's less used than
``.symlink`` nowadays, and a method named ".link" is easy to misinterpret.

I wanted a symbolic syntax for ``.chmod`` ("u=rwx,g+w") and a companion
function to parse a numeric mode, and user names/group names for ``.chown``,
but those were deferred to get the basic classes out the door.  The methods
take the same arguments as their ``os`` counterparts.
