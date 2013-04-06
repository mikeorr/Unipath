Unipath
%%%%%%%

An object-oriented approach to file/directory operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Version:           1.0
:Home page:         https://github.com/mikeorr/Unipath
:Docs:              https://github.com/mikeorr/Unipath#readme
:Author:            Mike Orr <sluggoster@gmail.com>
:License:           Python (http://www.python.org/psf/license)
:Based on:          path.py by Jason Orendorff, as modified for PEP 335
                    by Reinhold Birkenfeld and Björn Lindkvist. Influenced by
                    Noam Raphael's AlternativePathModule
:Contributors:      Ricardo Duarte

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
functionality. Unipath is stable, well-tested, and has been used in production
since 2008.

Version 1.0 runs on Python 2.6, 2.7, 3.2, and 3.3. Older Python versions should
stick to Unipath 0.2.

Users may also want to consider 'pathlib' (PEP 428), a more recent path library
which is being considered for inclusion in Python 3.4. It has a more modern
API, and I'm evaluating it as a potential successor to Unipath.  However, as of
March 2013 pathlib's API is still in flux, it has not been widely tested yet,
and it has fewer features than Unipath.

The ``Path`` class encapsulates the file/directory operations in Python's
``os``, ``os.path``, and ``shutil`` modules. (Non-filesystem operations are in
the ``AbstractPath`` superclass, but users can ignore this.)

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
    >>> print(p.read_file())
    The king is a fink!
    >>> d.rmtree()
    >>> p.exists()
    False

Path objects subclass ``str`` (Python 2 ``unicode``), so they can be passed
directly to fuctions expecting a string path. They are also immutable and can
be used as dictionary keys.

The name "Unipath" is short for "universal path". It was originally intended to
unify the competing path APIs as of PEP 334. When the PEP was rejected, Unipath
added some convenience APIs.  The code is implemented in layers, with
filesystem-dependent code in the ``Path`` class and filesystem-independent code
in its ``AbstractPath`` superclass.


Installation and testing
========================

Run "pip install Unipath".  Or to install the development version, check out
the source from the Git repository above and run "python setup.py develop".

To test the library, install 'pytest' and run "pytest test.py".  It also comes
with a Tox INI file.


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


Acknowledgments
===============

Jason Orendorff wrote the original path.py.  Reinhold Birkenfeld and
Björn Lindkvist modified it for Python PEP 335. Mike Orr changed the API and
released it as Unipath.  Ricardo Duarte ported it to Python 3, changed the
tests to py.test, and added Tox support.

Comparision with os/os.path/shutil and path.py
==============================================
::

    p = any path, f =  file, d = directory, l = link
    fsp, fsf, fsd, fsl = filesystem path (i.e., ``Path`` only)
    - = not implemented

Functions are listed in the same order as the Python Library Reference, version
2.5.  (Does not reflect later changes to Python or path.py.)

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
       [The rest of this footnote has been lost.]
.. [2] Closest equivalent is ``p.split_root()`` for approximate equivalent.
.. [3] More convenient alternatives exist.
.. [4] Inconvenient constants; not used enough to port.
.. [5] Chroot is more of an OS operation than a path operation.  Plus it's 
   dangerous.
.. [6] Ownership of symbolic link doesn't matter because the OS never 
   consults its permission bits.
.. [7] ``os.tempnam`` is insecure; use ``os.tmpfile`` or ``tempfile`` module
   instead.
.. [8] ``os.path.splitext(os.path.split(p))[0]``
.. [9] ``os.path.splitext(os.path.split(p))[1]``
.. [10] Closest equivalent is ``p.split_root()[0]``.
