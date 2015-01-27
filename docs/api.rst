API
%%%

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
