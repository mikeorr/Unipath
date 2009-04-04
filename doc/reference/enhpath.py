""" enhpath.py - An object-oriented approach to file/directory operations.

Author: Mike Orr <mso@oz.net>.
URL coming soon.

Derived from Jason Orendorff's path.py 2.0.4 (JOP) available at
http://www.jorendorff.com/articles/python/path.  

Whereas JOP maintains strict API compatibility with its parent functions,
enhpath ("enhanced path") stresses convenience and conciseness in the caller's
code.  It does this by combining related methods, encapsulating multistep
operations, and occasional magic behaviors.  Enhpath requires Python 2.3 (JOP:
Python 2.2).  Paths are subclasses of unicode, so all strings methods are
available too.  Redundant methods like .basename() are moved to subclass
path_compat.  Subclassable so you can add local methods.  (JOP: not
subclassable because methods that create new paths call path() directly rather
than self.__class__().)

Constructors and class methods:
  path('path/name')  path object
  path('')           Used to generate subpaths relative to current
                       directory: path('').joinpath('a') => path('a')
  path()             Same as path('')
  path.cwd()         Same as path(os.getcwd())
                       (JOP: path.getcwd() is static method)
  path.popdir(N=1)   Pop Nth previous directory off path.pushed_dirs, chdir to 
                       it, and log a debug message.  IndexError if we fall off
                       the end of the list.  See .chdir().  (JOP: no equiv.)
  path.tempfile(suffix='', prefix=tempfile.template, dir=None, text=False)
                     Create a temporary file using tempfile.mkstemp, open it,
                       and return a tuple of (path, file object).  The file
                       will not be automatically deleted.
                       'suffix': use this suffix; e.g., ".txt".
                       'prefix': use this prefix.
                       'dir': create in this directory (default system temp).
                       'text' (boolean): open in text mode.
                       (JOP: no equiv.)
  path.tempdir(suffix='', prefix=tempfile.template, dir=None)
                     Create a temporary directory using tempfile.mkdtemp and
                       return its path.  The directory will not be
                       automatically deleted.  (JOP: no equivalent.)
  path.tempfileobject(mode='w+b', bufsize=-1, suffix='', 
      prefix=tempfile.template, dir=None)
                     Return a file object pointing to an anonymous temporary
                       file.  The file will automatically be destroyed when the
                       file object is closed or garbage collected.  The file
                       will not be visible in the filesystem if the OS permits.
                       (Unix does.)  This is a static method since it neither
                       creates nor uses a path object.  The only reason it's in
                       this class is to put all the tempfile-creating methods
                       together.  (JOP: no equiv.)

Chdir warnings: changing the current working directory via path.popdir(),
.chdir(), or os.chdir() does not adjust existing relative path objects, so
if they're relative to the old current directory they're now invalid.  Changing
the directory is global to the runtime, so it's visible in all threads and
calling functions.

Class attributes:
  path.repr_as_str   True to make path('a').__repr__() return 'a'.  False
                       (default) to make it return 'path("a")'.  Useful when
                       you have to dump lists of paths or dicts containing
                       paths for debugging.  Changing this is visible in all
                       threads.  (JOP: no equivalent.)

Instance attributes:
  .parent      Parent directory as path.  Compare .ancestor().
                 path('a/b').parent => path('a').
                 path('b').parent => path('').
  .name        Filename portion as string.
                 path('a/filename.txt').name => 'filename.txt'.
  .base        Filename without extension.  Compare .stripext().
                 path('a/filename.txt').base => 'filename'.
                 path('a/archive.tar.gz').base => 'archive.tar'.
                 (JOP: called .namebase).
  .ext         Extension only.
                 path('a/filename.txt').ext => '.txt'.
                 path('a/archive.tar.gz').ext => '.gz'.

Interaction with Python operators:
  +            Simple concatenation.
                 path('a') + 'b' => path('ab').
                 'a' + path('b') => path('ab').
  /            Same as .joinpath().
                 path('a') / 'b' => path('a/b').
                 path('a') / 'b' / 'c' => path('a/b/c').

Normalization methods:
  .abspath()   Convert to absolute path.  Implies normpath on most platforms.
                 path('python2.4').abspath() => path('/usr/lib/python2.4').
  .isabs()     Is the path absolute?
  .normcase()  Does nothing on Unix.  On case-insensitive filesystems, converts
                 to lowercase.  On Windows, converts slashes to backslashes.
  .normpath()  Clean up .., ., redundant //, etc.  On Windows, convert shashes
                 to backslashes.  Python docs warn "this may change the meaning
                 of a path if it contains symbolic links!"
                 path('a/../b/./c//d').normpath() => path('b/c/d')
  .realpath()  Resolve symbolic links in path.
                 path('/home/joe').realpath() => path('/mnt/data/home/joe')
                 if /home is a symlink to /mnt/data/home.
  .expand()    Call expanduser, expandvars and normpath.  This is commonly
                 everything you need to clean up a filename from a 
                 configuration file.
  .expanduser() Convert ~user to the user's home directory.
                 path('~joe/Mail').expanduser() => path('/home/joe/Mail')
                 path('~/.vimrc').expanduser() => path('/home/joe/.vimrc')
  .expandvars() Resolve $ENVIRONMENT_VARIABLE references.
                 path('$HOME/Mail').expandvars() => path('/home/joe/Mail')
  .relpath()   Convert to relative path from current directory.
                 path('/home/joe/Mail') => path('Mail') if CWD is /home/joe.
  .relpathto(dest)  Return a relative path from self to dest.  If there is
                 no relative path (e.g., they reside on different drives on
                 Windows), same as dest.abspath().  Dest may be a path or a
                 string.
  .relpathfrom(ancestor)  Chop off the front part of self that matches 
                 ancestor.  
                 path('/home/joe/Mail').relpathfrom('/home/joe')  =>
                 path('Mail')
                 ValueError if self does not start with ancestor.

Deriving related paths:
  .splitpath()  Return a list of all directory/filename components.  The
                 first item will be a path, either os.curdir, os.pardir, empty,
                 or the root directory of this path (for example, '/' or
                 'C:\\').  The other items will be strings.
                 path('/usr/local/bin') => [path('/'), 'usr', 'local', 'bin']
                 path('a/b/c.txt') => [path(''), 'a', 'b', 'c.txt']
                 (JOP: This is what .splitall() does.  JOP's .splitpath()
                 returns (p.parent, p.name).)
                 (Note: not called .split() to avoid masking the string method
                 of that name.)
  .splitext()   Same as (p.stripext(), p.ext).
  .stripext()   Chop one extension off the path.
                  path('a/filename.txt').stripext() => path('a/filename')
  .joinpath(*components) Join components with directory separator as necessary.
                  path('a').joinpath('b', 'c') => path('a/b/c')
                  path('a/').joinpath('b') => path('a/b')
                  Calling .splitpath() and .joinpath() produces the original
                  path.
                  (Note: not called .join() to avoid masking the string method
                  of that name.)
  .ancestor(N)  Chop N components off end, same as invoking .parent N times.
                  path('a/b/c').ancestor(2) => path('a')
                  (JOP: no equivalent method.)
  .joinancestor(N, *components)
                Combination of .ancestor() and .joinpath().
                  (JOP: no equivalent method.)
  .redeploy(old_ancestor, new_ancestor)
                  Replace the old_ancestor part of self with new_ancestor.
                  Both may be paths or strings.  old_ancestor *must* be an
                  ancestor of self; this is checked via absolute paths even
                  if the specified paths are relative.  (Not implemented:
                  verifying it would be useful for things like Cheetah's --idir
                  and --odir options.)  (JOP: no equivalent method.)

Listing directories:
  Common arguments:  
                pattern, a glob pattern like "*.py".  Limits the result to
                  matching filenames.
                symlinks, False to exclude symbolic links from result.
                  Useful if you want to treat them separately.  (JOB: no 
                  equivalent argument.)

  .listdir(pattern=None, symlinks=True, names_only=False)  
                List directory.
                  path('/').listdir() => [path('/bin'), path('/boot'), ...]
                  path('/').listdir(names_only=True) => ['bin', 'boot', ...]
                  If names_only is true, symlinks is false and pattern is None,
                  this is the same as os.listdir() and no path objects are
                  created.  But if symlinks is true and there is a pattern,
                  it must create path objects to determine the return values,
                  and then turn them back to strings.
                  (JOP: No names_only argument.)
  .dirs(pattern=None, symlinks=True)
                List only the subdirectories in directory.  Not recursive.
                  path('/usr/lib/python2.3').dirs() => 
                    [path('/usr/lib/python2.3/site-packages'), ...]
  .files(pattern=None, symlinks=True)
                List only the regular files in directory.  Not recursive.
                  Does not list special files (anything for which
                  os.path.isfile() returns false).
                  path('/usr/lib/python2.3').dirs() => 
                    [path('/usr/lib/python2.3/BaseHTTPServer.py'), ...]
  .symlinks(pattern=None)
                List only the symbolic links in directory.  Not recursive.
                  path('/').symlinks() => [path('/home')] if it's a symlink.
                  (JOP: no equivalent method.)
  .walk(pattern=None, symlinks=True)
                Iterate over files and subdirs recursively.  The search is
                  depth-first.  Each directory is returned just before its
                  children.  Returns an iteration, not a list.
  .walkdirs(pattern=None, symlinks=True)
                Same as .walk() but yield only directories.
  .walkfiles(pattern=None, symlinks=True)
                Same as .walk() but yield only regular files.  Excludes
                  special files (anything for which os.path.isfile() returns
                  false).
  .walksymlinks(pattern=None)
                Same as .walk() but yield only symbolic links.
                  (JOP: no equivalent method.)
  .findpaths(args=None, ls=False, **kw) 
                Run the Unix 'find' command and return an iteration of paths.
                  The argument signature matches find's most popular arguments.
                  Due to Python's handling of keyword arguments, there are 
                  some limitations:
                    - You can't specify the same argument multiple times.
                    - The argument order may be rearranged.
                    - You can't do an 'or' expression or a 'brace' expression.
                    - Not all 'find' operations are implemented.
                  Special syntaxes:
                    - mtime=(N, N)
                      Converted to two -mtime options, used to specify a range.
                      Normally the first arg is negative and the second
                      positive.  Same for atime, ctime, mmin, amin, cmin.  
                    - name=[pattern1, pattern2, ...]
                      Converted to '-lbrace -name pattern1 -o ... -rbrace'.
                      Value may be list or tuple.
                  There are also some other arguments:
                    - args, list or string, appended to the shell command line.
                      Useful to do things the keyword args can't.  Note that
                      if value is a string, it is split on whitespace.
                    - ls, boolean, true to yield one-line strings describing
                      the files, same as find's '-ls' option.  Does not yield
                      paths.
                    - pretend, boolean, don't run the command, just return it
                      as a string.  Useful only for debugging.  We try to
                      handle quoting intelligently but there's no guarantee
                      we'll produce a valid or correct command line.  If your
                      argument values have quotes, spaces, or newlines, use
                      pretend=True and verify the command line is correct,
                      otherwise you may have unexpected problems.  If 'pretend'
                      is False (default), the subcommand is logged to the
                      'enhpath' logger, level debug.  See Python's 'logging'
                      module for details.
                  Examples:
                  .find(name='*.py')
                  .find(type='d', ls=True)
                  .find(mtime=-1, type='f')
                  (JOP: no equivalent method.)

                  WARNING: Normally we bypass the shell to avoid quoting
                  problems.  However, if 'args' is a string or we're running on
                  Python 2.3, we can't avoid the shell.  Argument values
                  containing spaces, quotes, or newlines may be misinterpreted
                  by the shell.  This can lead to a syntax error or to an
                  incorrect search.  When in doubt, use the 'pretend' argument
                  to verify the command line is correct.

                  path('').find(...) yields paths relative to the current
                  directory.  In this case, 'find' on posix returns paths
                  prefixed with "./", so we chop off this prefix.  We don't
                  call .normpath() because of its fragility with symbolic
                  links.  On other platforms we don't clean up the paths
                  because we don't know how.
                  
  .findpaths_pretend(args=None, ls=False, **kw) 
                Same as .find(...) above but don't actually do the find;
                  instead, return the external command line as a list of
                  strings.  Useful for debugging.
  .fnmatch(pattern)  Return True if self.name matches the pattern.
  .glob(pattern)  Return a list of paths that match the pattern.
                  path('a').glob('*.py') => Same as path('a').listdir('*.py')
                  path('a').glob('*/bin/*') => List of files all users have 
                                               in their bin directories.

# Reading/writing files                
  .open(mode='r')   Open file and return a file object.
  .file(mode='r')   Same.
  .bytes(mode='r')  Read the file in binary mode and return content as string.
  .write_bytes(bytes, append=False)
                    Write 'bytes' (string) to the file.  Overwrites the file
                      unless 'append' is true.
  .text(encoding=None, errors='strict')
                    Read the file in text mode and return content as string.
                      'encoding' is a Unicode encoding/character set.  If
                      present, the content is returned as a unicode object;
                      otherwise it's returned as an 8-bit string.
                      'errors' is an argument for str.decode().
  .write_text(text, encoding=None, errors='strict', linesep=os.linesep,
      append=False)
                   Write 'text' (string) to the file in text mode.  Overwrites
                     the file unless 'append' (keyword arg) is true.
                     'encoding' (string) is the unicode encoding.  Ignored if
                     text is string type rather than unicode type.
                     'errors' is an argument for unicode.encode().
                     'linesep' (keyword arg) the chars to write for newline.
                     None means don't convert newlines.  The default is your
                     platform's preferred  convention.
  .lines(encoding=None, errors='strict', retain=True)
                   Read the file in text mode and return the lines as a list.
                     'encoding' and 'errors' are same as for .text().
                     'retain' (boolean) If true, convert all newline types to
                     '\n'.  If false, chop off newlines.
                     The open mode is 'U'.
                     To iterate over the lines, use the filehandle returned by
                     .open() as an iterator.
  .writelines(lines, encoding=None, errors='strict', linesep=os.linesep,
       append=False)
                   Write the lines (list) to the file.
                     The other args are the same as for .write_text().
                     When appending, use the same Unicode encoding the original
                     text was written in, otherwise the reader will be very
                     confused.

Checking file existence/type:
  .exists()       Does the path exist?
  .isdir()        Is the path a directory?
  .isfile()       Is the path a regular file?
  .islink()       Is the path a symbolic link?
  .ismount()      Is the path a mount point?
  .isspecial()    Is the path a special file?
  .type()         Return the file type using the one-letter codes from the
                    'find' command:
                    'f'  => regular file             (path.FILE)
                    'd'  => directory                (path.DIR)
                    'l'  => symbolic link            (path.LINK)
                    'b'  => block special file       (path.BLOCK)
                    'c'  => character special file   (path.CHAR)
                    'p'  => named pipe/FIFO          (path.PIPE)
                    's'  => socket                   (path.SOCKET)
                    'D'  => Door (Solaris)           (path.DOOR)
                    None => unknown
                    The constants at the right are class attributes if you
                    prefer to compare to them instead of literal chars.  You'll
                    never get a 'D' in the current implementation since the
                    'stat' module provides no way to test for a Door.
                    path.SPECIAL_TYPES is a list of the latter five types.
All the .is*() functions return False if the path doesn't exist.  All except
.islink() return the state of the pointed-to file if the path is a symbolic
link.  .isfile() returns False for a special file.  To test a special file's
type, pass .stat().st_mode to one of the S_*() functions in the 'stat' module;
this is more efficient than .isspecial() when you only care about one type.
                     
Checking permissions and other information:
  .stat()         Get general file information; see os.stat().
  .lstat()        Same as .stat() but don't follow a symbolic link.
  .statvfs()      Get general information about the filesystem; see
                    os.statvfs().
  .samefile(other)  Is self and other the same file?  Returns True if one is
                    a symbolic or hard link to the other.  'other' may be a 
                    path or a string.
  .pathconf(name) See os.pathconf(); OS-specific info about the path.
  .canread()      Can we read the file?  (JOP: no equivalent.)
  .canwrite()     Can we write the file? (JOP: no equivalent.)
  .canexecute()   Can we execute the file?  True for a directory means we
                    can chdir into it or access its contents. 
                    (JOP: no equivalent.)
  .access(mode)   General permission test; see os.access() for usage.

Modifying file information:
  .utime(times)   Set file access and modification time.
                    'time' is either None to set them to the current time, or
                    a tuple of (atime, mtime) -- integers in tick
                    format (the same format returned by time.time()).
  .getutime()     Return a tuple of (atime, mtime).  This can be passed 
                    directly to another path's .utime().  (JOP: no equiv.)
  .copyutimefrom(other)  Make my atime/mtime match the other path's.
                    'other' may be a path or a string.  (JOP: no equiv.)
  .copyutimeto(*other)    Make the other paths' atime/mtime match mine.
                    Note that multiple others can be specified, unlike
                    .copyutimefrom().  (JOP: no equiv.)
  .itercopyutimeto(iterpaths)  Same as .copyutimeto() but use an iterable to
                    specify the destination paths.  (JOP: no equiv.)
  .chmod(mode)    Set the path's permissions to 'mode' (octal int).
                    There are several constants in the 'stat' module you can
                    use; use the '|' operator to combine them.
  .grant(mode)    Add 'mode' to the file's current mode.  (Uses '|'.)
  .grant(mode)    Subtract 'mode' from the file's current mode.  (Uses '&'.)
  .chown(uid=None, gid=None)  Change the path's owner/group.
                    If uid or gid is a string, look up the corresponding
                    number via the 'pwd' or 'group' module.  
                    (JOP: both uid and gid must be specified, and both must
                    be numeric.)
  .needsupdate(*other)  
                  True if the path doesn't exist or its mtime is older
                    than any of the others.  If any 'other' is a directory,
                    only the directory mtime will be compared; this method
                    does not recurse.  A directory's mtime changes when a
                    file in it is added, removed, or renamed.  To do the 
                    equvalent of iteration, see .iterneedsupdate().
                    (JOP: no equivalent method.)
  .iterneedsupdate(iterpaths)  
                  Same as .needsupdate() but use an iterable to
                    specify the other paths.  To do the equivalent of a 
                    recursive compare, call .walkfiles() on the other
                    directories and concatenate the iterators using 
                    itertools.chain, interspersing any static lists of paths
                    you wish.  (JOP: no equivalent method.)
                    
Moving files and directories:
  .move(dest, overwrite=True, prune=False, atomic=False)     
                 Move the file or directory to 'dest'.
                    Tries os.rename() or os.renames() first, falls back to
                    shutil.move() if it fails.
                    If 'overwrite' is false, raise OverwriteError if dest
                    exists.
                    Creates any ancestor directories of dest if missing.
                    If 'prune' is true, delete any empty ancestor parent
                    directories of source after move.
                    If 'atomic' is true and .rename*() fails, don't catch the
                    OSError and don't try shutil.move().  This guarantees that
                    if the move succeeds, it's an atomic operation.  This will
                    fail if the two paths are on different filesystems, and
                    may fail if the source is a directory.
                    (JOP: this combines the functionality of .rename(),
                    .renames(), and .move().)
  .movefile(dest, overwrite=True, prune=False, atomic=False, checkdest=False)
               Same as .move() but raise FileTypeError if path is a file
                 rather than a directory.
                 'checkdest' (boolean) True to fail dest is a file.
                 (JOP: no equivalent method.)
  .movedir(dest, overwrite=True, prune=False, atomic=False, checkdest=False)
               Same as .move() but raise FileTypeError if path is a directory.
                 'checkdest' (boolean) True to fail dest is a directory.
                 (JOP: no equivalent method.)

Creating directories and (empty) files:
  .mkdir(mode=0777, clobber=False)
               Create an empty directory.
                 If 'clobber' is true, call .delete_dammit() first.  Otherwise
                 you'll get OSError if a file exists in its place.
                 Silently succeed if the directory exists and clobber is false.
                 Creates any missing ancestor directories.
                 (JOP: this is equivalent to .makedirs() rather than
                 .makedir(), except you'll get OSError if a directory or file
                 exists.)
  .touch()     Create a file if it doesn't exist.  If a file or directory does
                 exist, set its atime and mtime to the current time -- same as
                 .utime(None).

Deleting directories and files:
  .delete_dammit()
               Delete path recursively whatever it is, and don't complain if
                 it doesn't exist.  Convenient but dangerous!
                 (JOP: combines .rmtree(), .rmdir(), and .remove(), plus unqiue
                 features.)
  .rmdir(prune=False)     
               Delete a directory.
                 Silently succeeds if it doesn't exist.  OSError if it's a file
                 or symbolic link.  See .delete_dammit().  
                 If 'prune' is true, also delete any empty ancestor
                 directories.
                 (JOP: equivalent to .removedirs() if prune is true, or
                 .rmdir() if prune is false, except the JOP methods don't have
                 a 'prune' argument, and they raise OSError if the directory
                 doesn't exist.)
  .remove(prune=False)    
              Delete a file.
                 Silently succeeds if it doesn't exist.  OSError if it's a 
                 directory.
                 If 'prune' is true, delete any ancestor directories.
                 (JOP: equivalent to .remove() if prune is false, except JOP
                 method has no 'prune' arg.  Raises OSError if it doesn't 
                 exist.)
   .unlink(prune=False)  Same as .remove().

Links:
  .hardlink(source)
                 Create a hard link at 'source' pointing to this path.
                 (JOP: equivalent to .link().)
  .symlink(source)
                 Create a symbolic link at 'source' pointing to this path.
                   If path is relative, it should be relative to source's
                   directory, but it needn't be valid with the current
                   directory. 
  .readlink()   Return the path this symbolic link points to.
  .readlinkabs()  Same as .readlink() but always return an absolute path.

Copying files and directories:
  .copy(dest, copy_times=True, copy_mode=False, symlinks=True)
                Copy a file or (recursively) a directory.
                  If 'copy_times' is true (default), copy the atime/mtime too.
                  If 'copy_mode' is true (not default), copy the permission
                  bits too.
                  If 'symlinks' is true (default), create symbolic links in
                  dest corresponding to those in path (using shutil.copytree,
                  which does not claim infallibility).
                  (JOP: combines .copy(), .copy2(), .copytree().)
  .copymode(dest)
                Copy path's permission bits to dest (but not its content).
  .copystat(dest)
                Copy path's permission bits and atime/mtime to dest (but not
                  its content or owner/group).  Overlaps with .copyutimeto().  

Modifying the runtime environment:
  .chdir(push=False)      
                Set the current working directory to path.
                  If 'push' is true, push the old current directory onto
                  path.pushed_dirs (class attribute) and log a debug message.
                  Note that pushing is visible to all threads and calling
                  functions.  (JOP: no equiv.)
  .chroot()     Set this process's root directory to path.


Subclass path_windows(path):   # Windows-only operations.
  .drive       Drive specification.
                 path('C:\COMMAND.COM') => 'C:' on Windows, '' on Unix.
  .splitdrive() Same as (p.drive, path(p.<everything else>))
  .splitunc()   Same as (p.uncshare, path(p.<everything else>)
  .uncshare     The UNC mount point, empty for local drives.  UNC files are
                  in \\host\path syntax.
  .startfile()  Launch path as an autonoymous program (Windows only).

Subclass path_compat(path_windows):  # Redundant JOP methods.
  .namebase()    Same as .base.
  .basename()    Same as .name.
  .dirname()     Same as .parent.
  .getatime()    Same as .atime.
  .getmtime()    Same as .mtime.
  .getctime()    Same as .ctime.
  .getsize()     Same as .size.

# JOP has the following TODO, which I suppose applies here too:
#   - Bug in write_text().  It doesn't support Universal newline mode.
#   - Better error message in listdir() when self isn't a
#     directory. (On Windows, the error message really sucks.)
#   - Make sure everything has a good docstring.
#   - Add methods for regex find and replace.
#   - guess_content_type() method?
#   - Perhaps support arguments to touch().
#   - Could add split() and join() methods that generate warnings.
#   - Note:  __add__() technically has a bug, I think, where
#     it doesn't play nice with other types that implement
#     __radd__().  Test this.
"""
import codecs, fnmatch, glob, os, shutil, stat, sys
import tempfile as _tempfile # Avoid conflicts with same-name method.

__version__ = '0.1'
__all__ = ['path']

_base = os.path.supports_unicode_filenames and unicode or str
_textmode = hasattr(file, 'newlines') and 'U' or 'r'

class path(_base):
    #### Constants
    # File types returned by .type() and accepted by .specials() and .find().
    FILE   = 'f'
    DIR    = 'd'
    LINK   = 'l'
    CHAR   = 'c'
    BLOCK  = 'b'
    PIPE   = 'p'
    SOCKET = 's'
    DOOR   = 'D'
    SPECIAL_TYPES = [CHAR, BLOCK, PIPE, SOCKET, DOOR]

    #### Flags and other class attributes
    repr_as_str = False
    pushed_dirs = [] # Shared list of pushed directories.

    # --- Special Python methods.

    def __repr__(self):
        if self.repr_as_str:
            return self.__str__().__repr__()
        else:
            return 'path(%s)' % _base.__repr__(self)

    # Adding a path and a string yields a path.
    def __add__(self, more):
        return self.__class__(_base(self) + more)

    def __radd__(self, other):
        return self.__class__(other + _base(self))

    # The / operator joins paths.
    def __div__(self, rel):
        """ fp.__div__(rel) == fp / rel == fp.joinpath(rel)

        Join two path components, adding a separator character if
        needed.
        """
        return self.__class__(os.path.join(self, rel))

    # Make the / operator work even when true division is enabled.
    __truediv__ = __div__

    # Class methods (alternate constructors) and static methods.
    def cwd(klass):
        """ Return the current working directory as a path object. """
        return klass(os.getcwd())
    cwd = classmethod(cwd)

    def popdir(klass, n=1):
        for i in range(n):
            dir = klass.pushed_dirs.pop()
        os.chdir(dir)
    popdir = classmethod(popdir)

    def tempfile(klass, suffix='', prefix=_tempfile.template, dir=None, 
        text=False):
        fil = _tempfile.mkstemp(suffix, prefix, dir, text)
        return klass(fil)
    tempfile = classmethod(tempfile)

    def tempdir(klass, suffix='', prefix=_tempfile.template, dir=None):
        dir = _tempfile.mkdtemp(suffix, prefix, dir)
        return klass(dir)
    tempdir = classmethod(tempdir)

    def tempfileobject(mode='w+b', bufsize=-1, suffix='', 
        prefix=_tempfile.template, dir=None):
        f = _tempfile.TemporaryFile(mode, bufsize, suffix, prefix, dir)
        return f
    tempfileobject = staticmethod(tempfileobject)


    # --- Operations on path strings.

    def abspath(self):       return self.__class__(os.path.abspath(self))
    def normcase(self):      return self.__class__(os.path.normcase(self))
    def normpath(self):      return self.__class__(os.path.normpath(self))
    def realpath(self):      return self.__class__(os.path.realpath(self))
    def expanduser(self):    return self.__class__(os.path.expanduser(self))
    def expandvars(self):    return self.__class__(os.path.expandvars(self))
    def dirname(self):       return self.__class__(os.path.dirname(self))
    basename = os.path.basename

    def expand(self):
        """ Clean up a filename by calling expandvars(),
        expanduser(), and normpath() on it.

        This is commonly everything needed to clean up a filename
        read from a configuration file, for example.
        """
        return self.expandvars().expanduser().normpath()

    def _get_base(self):
        base, ext = os.path.splitext(self.name)
        return base

    def _get_ext(self):
        f, ext = os.path.splitext(_base(self))
        return ext

    def _get_drive(self):
        drive, r = os.path.splitdrive(self)
        return self.__class__(drive)

    parent = property(
        dirname, None, None,
        """ This path's parent directory, as a new path object.

        For example, path('/usr/local/lib/libpython.so').parent == path('/usr/local/lib')
        """)

    name = property(
        basename, None, None,
        """ The name of this file or directory without the full path.

        For example, path('/usr/local/lib/libpython.so').name == 'libpython.so'
        """)

    base = property(
        _get_base, None, None,
        """ The same as path.name, but with one file extension stripped off.

        For example, path('/home/guido/python.tar.gz').name     == 'python.tar.gz',
        but          path('/home/guido/python.tar.gz').namebase == 'python.tar'
        """)

    ext = property(
        _get_ext, None, None,
        """ The file extension, for example '.py'. """)

    drive = property(
        _get_drive, None, None,
        """ The drive specifier, for example 'C:'.
        This is always empty on systems that don't use drive specifiers.
        """)

    def splitdrive(self):
        """ p.splitdrive() -> Return (p.drive, <the rest of p>).

        Split the drive specifier from this path.  If there is
        no drive specifier, p.drive is empty, so the return value
        is simply (path(''), p).  This is always the case on Unix.
        """
        drive, rel = os.path.splitdrive(self)
        return self.__class__(drive), rel

    def splitpath(self):
        """ Return a list of the path components in this path.

        The first item in the list will be a path.  Its value will be
        either os.curdir, os.pardir, empty, or the root directory of
        this path (for example, '/' or 'C:\\').  The other items in
        the list will be strings.

        path.path.joinpath(*result) will yield the original path.
        """
        parts = []
        loc = self
        while loc != os.curdir and loc != os.pardir:
            prev = loc
            loc, child = os.path.split(prev)
            loc = self.__class__(loc)
            if loc == prev:
                break
            parts.append(child)
        parts.append(loc)
        parts.reverse()
        return parts

    def splitext(self):
        """ p.splitext() -> Return (p.stripext(), p.ext).

        Split the filename extension from this path and return
        the two parts.  Either part may be empty.

        The extension is everything from '.' to the end of the
        last path segment.  This has the property that if
        (a, b) == p.splitext(), then a + b == p.
        """
        filename, ext = os.path.splitext(self)
        return self.__class__(filename), ext

    def stripext(self):
        """ p.stripext() -> Remove one file extension from the path.

        For example, path('/home/guido/python.tar.gz').stripext()
        returns path('/home/guido/python.tar').
        """
        return self.splitext()[0]

    if hasattr(os.path, 'splitunc'):
        def splitunc(self):
            unc, rest = os.path.splitunc(self)
            return self.__class__(unc), rest

        def _get_uncshare(self):
            unc, r = os.path.splitunc(self)
            return self.__class__(unc)

        uncshare = property(
            _get_uncshare, None, None,
            """ The UNC mount point for this path.
            This is empty for paths on local drives. """)

    def joinpath(self, *components):
        """ Join two or more path components, adding a separator
        character (os.sep) if needed.  Returns a new path
        object.
        """
        return self.__class__(os.path.join(self, *components))

    def ancestor(self, n):
        p = self
        for i in range(n):
            p = p.parent
        return p

    def joinancestor(self, n, *components):
        return self.ancestor(n).joinpath(*components)

    def relpath(self):
        """ Return this path as a relative path,
        based from the current working directory.
        """
        cwd = self.__class__(os.getcwd())
        return cwd.relpathto(self)

    def relpathto(self, dest):
        """ Return a relative path from self to dest.

        If there is no relative path from self to dest, for example if
        they reside on different drives in Windows, then this returns
        dest.abspath().
        """
        origin = self.abspath()
        dest = self.__class__(dest).abspath()

        orig_list = origin.normcase().splitpath()
        # Don't normcase dest!  We want to preserve the case.
        dest_list = dest.splitpath()

        if orig_list[0] != os.path.normcase(dest_list[0]):
            # Can't get here from there.
            return dest

        # Find the location where the two paths start to differ.
        i = 0
        for start_seg, dest_seg in zip(orig_list, dest_list):
            if start_seg != os.path.normcase(dest_seg):
                break
            i += 1

        # Now i is the point where the two paths diverge.
        # Need a certain number of "os.pardir"s to work up
        # from the origin to the point of divergence.
        segments = [os.pardir] * (len(orig_list) - i)
        # Need to add the diverging part of dest_list.
        segments += dest_list[i:]
        if len(segments) == 0:
            # If they happen to be identical, use os.curdir.
            return self.__class__(os.curdir)
        else:
            return self.__class__(os.path.join(*segments))

    def relpathfrom(self, ancestor):
        """ Chop off the prefix of self that matches ancestor.

            path('/home/joe/Mail').relpathfrom('/home/joe')  =>
            path('Mail')
            ValueError if self does not start with ancestor.
        """
        if not ancestor.endswith(os.sep):
            ancestor += os.sep
        if not self.startswith(ancestor):
            raise ValueError("arg is not an ancestor of self")
        ancestor_len = len(ancestor)
        return path(self[ancestor_len:])

    def reparent(self, oldparent, newparent=None):
        """ Strip directory prefix 'oldparent' and subtitute 'newparent'.

            The first part of 'self' must equal 'oldparent' and be followed by
            the path separator.  E.g., if str(oldparent) is "a/b", str(self)
            must start with "a/b/", otherwise ValueError.

            If 'newparent' is omitted, make 'self' relative to 'oldparent'.

            The arguments may be any ancestor, not just the immediate patent.
        """
        if newparent is None:
            newparent = emptypath
        prefix = oldparent + os.sep
        if not self.startswith(prefix):
            msg = "path '%s' does not start with prefix '%s'" % (self, prefix)
            raise ValueError(msg)
        return newparent / self[len(prefix):]


    # --- Listing, searching, walking, and matching

    def listdir(self, pattern=None, symlinks=True, names_only=False):
        """ D.listdir() -> List of items in this directory.

        Use D.files() or D.dirs() instead if you want a listing
        of just files or just subdirectories.

        The elements of the list are path objects.

        With the optional 'pattern' argument, this only lists
        items whose names match the given pattern.

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        names = os.listdir(self or os.curdir)
        if names_only and not pattern and not symlinks:
            return names
        if pattern is not None:
            names = fnmatch.filter(names, pattern)
        if symlinks:
            paths = [self / child for child in names]
        else:
            # The code below works whether 'symlinks' is true or false.  If
            # true, it's less efficient than the list interpolation above.  If
            # false, it's *more* efficient than adding if symlink or not
            # (self/child).islink() to the interpolation because the path is
            # created only once.
            paths = []
            for child in names:
                p = self / child
                if symlinks or not p.islink():
                    paths.append(p)
        if names_only:
            return [p.name for p in paths]
        else:
            return paths

    def dirs(self, pattern=None, symlinks=True):
        """ D.dirs() -> List of this directory's subdirectories.

        The elements of the list are path objects.
        This does not walk recursively into subdirectories
        (but see path.walkdirs).

        With the optional 'pattern' argument, this only lists
        directories whose names match the given pattern.  For
        example, d.dirs('build-*').

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        return [p for p in self.listdir(pattern, symlinks) if p.isdir()]

    def files(self, pattern=None, symlinks=True):
        """ D.files() -> List of the files in this directory.

        The elements of the list are path objects.
        This does not walk into subdirectories (see path.walkfiles).

        With the optional 'pattern' argument, this only lists files
        whose names match the given pattern.  For example,
        d.files('*.pyc').

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        
        return [p for p in self.listdir(pattern, symlinks) if p.isfile()]

    def symlinks(self, pattern=None):
        """ D.symlinks() -> List of the symbolic links in this directory.

        The elements of the list are path objects.
        This does not walk into subdirectories (see path.walklinks).

        With the optional 'pattern' argument, this only lists files
        whose names match the given pattern.  For example,
        d.files('*.pyc').
        """
        
        return [p for p in self.listdir(pattern, True) if p.islink()]

    def walk(self, pattern=None, symlinks=True):
        """ D.walk() -> iterator over files and subdirs, recursively.

        The iterator yields path objects naming each child item of
        this directory and its descendants.  This requires that
        D.isdir().

        This performs a depth-first traversal of the directory tree.
        Each directory is returned just before all its children.

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        for child in self.listdir(symlinks=symlinks):
            if pattern is None or child.fnmatch(pattern):
                yield child
            if child.isdir():
                for item in child.walk(pattern):
                    yield item

    def walkdirs(self, pattern=None, symlinks=True):
        """ D.walkdirs() -> iterator over subdirs, recursively.

        With the optional 'pattern' argument, this yields only
        directories whose names match the given pattern.  For
        example, mydir.walkdirs('*test') yields only directories
        with names ending in 'test'.

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        for child in self.dirs(symlinks=symlinks):
            if pattern is None or child.fnmatch(pattern):
                yield child
            for subsubdir in child.walkdirs(pattern):
                yield subsubdir

    def walkfiles(self, pattern=None, symlinks=True):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.

        If 'symlinks' is false, exclude symbolic links from the result.
        """
        for child in self.listdir(symlinks=symlinks):
            if child.isfile():
                if pattern is None or child.fnmatch(pattern):
                    yield child
            elif child.isdir():
                for f in child.walkfiles(pattern):
                    yield f

    def walksymlinks(self, pattern=None, symlinks=True):
        """ D.walksymlinks() -> iterator over symbolic links in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
        for child in self.listdir(symlinks=True):
            if child.islink():
                if child.isfile():
                    if pattern is None or child.fnmatch(pattern):
                        yield child
                elif child.isdir():
                    for f in child.walkfiles(pattern):
                        yield f

    walklinks = walksymlinks

    def findpaths_pretend(self, args=None, ls=False, **kw):
        if isinstance(args, str):
            args = args.split()
        try:
            import subprocess
            has_subprocess = True
        except ImportError:
            has_subprocess = False
        cmd = ['find', str(self)]
        sequence_types = list, tuple
        # One-arg options we expand into OR expressions if value is multiple.
        for key in ['name']:
            if key in kw:
                option = '-' + key
                value = kw[key]
                if isinstance(value, sequence_types):
                    cmd.append('-lbrace')
                    for v in value[:-1]:
                        cmd.append(option)
                        cmd.append(str(v))
                        cmd.append('-or')
                    cmd.append(option)
                    cmd.append(str(value[-1]))
                    cmd.append('-rbrace')
                else:
                    cmd.extend([option, value])
        # One-arg options.
        for key in ['type', 'maxdepth', 'mindepth', 'newer', 'anewer',
            'cnewer', 'empty', 'fstype', 'gid', 'group', 'iname', 'lname',
            'ilname', 'inum', 'path', 'ipath', 'regex', 'iregex', 'links',
            'perm', 'size', 'uid', 'user', 'xtype']:
            if key in kw:
                option = '-' + key
                value = str(kw[key])
                cmd.extend([option, value])
        # One-arg options we can double if the value is a 2-tuple.
        for key in ['mtime', 'atime', 'ctime', 'mmin', 'amin', 'cmin']:
            if key in kw:
                option = '-' + key
                value = kw[key]
                if isinstance(value, sequence_types):
                    if len(value) == 2:
                        lis = [option, str(value[0]), option, str(value[1])]
                        cmd.extend(lis)
                    else:
                        msg = "arg '%s' must be string or 2-tuple" % key
                        raise ValueError(msg)
                else:
                    cmd.extend([option, str(value)])
        # No-arg options.
        for key in ['daystart', 'depth', 'follow', 'mount', 'xdev', 'noleaf',
            'nouser', 'nogroup']:
            if kw.get(key): # If key exists and value is true.
                option = '-' + key
                cmd.append(option)
        if args:
            if isinstance(args, sequence_types):
                args = map(str, args)
                cmd.extend(args)
            else:
                cmd.append(str(args))
                shell = True
        if ls:
            cmd.append('-dir')
        return cmd

    def findpaths(self, args=None, ls=False, **kw):
        cmd = self.findpaths_pretend(args, ls, **kw)
        try:
            import subprocess
        except ImportError:
            cmd = ' '.join(cmd)
            p = os.popen(cmd, 'r')
            f = p
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            f = p.stdout
        for lin in f:
            lin = lin.rstrip()
            if lin.startswith('./'):
                lin = lin[2:]
            yield lin

    def fnmatch(self, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards,
            for example '*.py'.
        """
        return fnmatch.fnmatch(self.name, pattern)

    def glob(self, pattern):
        """ Return a list of path objects that match the pattern.

        pattern - a path relative to this directory, with wildcards.

        For example, path('/users').glob('*/bin/*') returns a list
        of all the files users have in their bin directories.
        """
        return map(path, glob.glob(_base(self / pattern)))


    # --- Reading or writing an entire file at once.

    def open(self, mode='r'):
        """ Open this file.  Return a file object. """
        return file(self, mode)
        
    file = open

    def bytes(self):
        """ Open this file, read all bytes, return them as a string. """
        f = self.open('rb')
        try:
            return f.read()
        finally:
            f.close()

    def write_bytes(self, bytes, append=False):
        """ Open this file and write the given bytes to it.

        Default behavior is to overwrite any existing file.
        Call this with write_bytes(bytes, append=True) to append instead.
        """
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        f = self.open(mode)
        try:
            f.write(bytes)
        finally:
            f.close()

    def text(self, encoding=None, errors='strict'):
        """ Open this file, read it in, return the content as a string.

        This uses 'U' mode in Python 2.3 and later, so '\r\n' and '\r'
        are automatically translated to '\n'.

        Optional arguments:

        encoding - The Unicode encoding (or character set) of
            the file.  If present, the content of the file is
            decoded and returned as a unicode object; otherwise
            it is returned as an 8-bit str.
        errors - How to handle Unicode errors; see help(str.decode)
            for the options.  Default is 'strict'.
        """
        if encoding is None:
            # 8-bit
            f = self.open(_textmode)
            try:
                return f.read()
            finally:
                f.close()
        else:
            # Unicode
            f = codecs.open(self, 'r', encoding, errors)
            # (Note - Can't use 'U' mode here, since codecs.open
            # doesn't support 'U' mode, even in Python 2.3.)
            try:
                t = f.read()
            finally:
                f.close()
            return (t.replace(u'\r\n', u'\n')
                     .replace(u'\r\x85', u'\n')
                     .replace(u'\r', u'\n')
                     .replace(u'\x85', u'\n')
                     .replace(u'\u2028', u'\n'))

    def write_text(self, text, encoding=None, errors='strict', linesep=os.linesep, append=False):
        """ Write the given text to this file.

        The default behavior is to overwrite any existing file;
        to append instead, use the 'append=True' keyword argument.

        There are two differences between path.write_text() and
        path.write_bytes(): newline handling and Unicode handling.
        See below.

        Parameters:

          - text - str/unicode - The text to be written.

          - encoding - str - The Unicode encoding that will be used.
            This is ignored if 'text' isn't a Unicode string.

          - errors - str - How to handle Unicode encoding errors.
            Default is 'strict'.  See help(unicode.encode) for the
            options.  This is ignored if 'text' isn't a Unicode
            string.

          - linesep - keyword argument - str/unicode - The sequence of
            characters to be used to mark end-of-line.  The default is
            os.linesep.  You can also specify None; this means to
            leave all newlines as they are in 'text'.

          - append - keyword argument - bool - Specifies what to do if
            the file already exists (True: append to the end of it;
            False: overwrite it.)  The default is False.


        --- Newline handling.

        write_text() converts all standard end-of-line sequences
        ('\n', '\r', and '\r\n') to your platform's default end-of-line
        sequence (see os.linesep; on Windows, for example, the
        end-of-line marker is '\r\n').

        If you don't like your platform's default, you can override it
        using the 'linesep=' keyword argument.  If you specifically want
        write_text() to preserve the newlines as-is, use 'linesep=None'.

        This applies to Unicode text the same as to 8-bit text, except
        there are three additional standard Unicode end-of-line sequences:
        u'\x85', u'\r\x85', and u'\u2028'.

        (This is slightly different from when you open a file for
        writing with fopen(filename, "w") in C or file(filename, 'w')
        in Python.)


        --- Unicode

        If 'text' isn't Unicode, then apart from newline handling, the
        bytes are written verbatim to the file.  The 'encoding' and
        'errors' arguments are not used and must be omitted.

        If 'text' is Unicode, it is first converted to bytes using the
        specified 'encoding' (or the default encoding if 'encoding'
        isn't specified).  The 'errors' argument applies only to this
        conversion.

        """
        if isinstance(text, unicode):
            if linesep is not None:
                # Convert all standard end-of-line sequences to
                # ordinary newline characters.
                text = (text.replace(u'\r\n', u'\n')
                            .replace(u'\r\x85', u'\n')
                            .replace(u'\r', u'\n')
                            .replace(u'\x85', u'\n')
                            .replace(u'\u2028', u'\n'))
                text = text.replace(u'\n', linesep)
            if encoding is None:
                encoding = sys.getdefaultencoding()
            bytes = text.encode(encoding, errors)
        else:
            # It is an error to specify an encoding if 'text' is
            # an 8-bit string.
            assert encoding is None

            if linesep is not None:
                text = (text.replace('\r\n', '\n')
                            .replace('\r', '\n'))
                bytes = text.replace('\n', linesep)

        self.write_bytes(bytes, append)

    def lines(self, encoding=None, errors='strict', retain=True):
        """ Open this file, read all lines, return them in a list.

        Optional arguments:
            encoding - The Unicode encoding (or character set) of
                the file.  The default is None, meaning the content
                of the file is read as 8-bit characters and returned
                as a list of (non-Unicode) str objects.
            errors - How to handle Unicode errors; see help(str.decode)
                for the options.  Default is 'strict'
            retain - If true, retain newline characters; but all newline
                character combinations ('\r', '\n', '\r\n') are
                translated to '\n'.  If false, newline characters are
                stripped off.  Default is True.

        This uses 'U' mode in Python 2.3 and later.
        """
        if encoding is None and retain:
            f = self.open(_textmode)
            try:
                return f.readlines()
            finally:
                f.close()
        else:
            return self.text(encoding, errors).splitlines(retain)

    def write_lines(self, lines, encoding=None, errors='strict',
                    linesep=os.linesep, append=False):
        """ Write the given lines of text to this file.

        By default this overwrites any existing file at this path.

        This puts a platform-specific newline sequence on every line.
        See 'linesep' below.

        lines - A list of strings.

        encoding - A Unicode encoding to use.  This applies only if
            'lines' contains any Unicode strings.

        errors - How to handle errors in Unicode encoding.  This
            also applies only to Unicode strings.

        linesep - The desired line-ending.  This line-ending is
            applied to every line.  If a line already has any
            standard line ending ('\r', '\n', '\r\n', u'\x85',
            u'\r\x85', u'\u2028'), that will be stripped off and
            this will be used instead.  The default is os.linesep,
            which is platform-dependent ('\r\n' on Windows, '\n' on
            Unix, etc.)  Specify None to write the lines as-is,
            like file.writelines().

        Use the keyword argument append=True to append lines to the
        file.  The default is to overwrite the file.  Warning:
        When you use this with Unicode data, if the encoding of the
        existing data in the file is different from the encoding
        you specify with the encoding= parameter, the result is
        mixed-encoding data, which can really confuse someone trying
        to read the file later.
        """
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        f = self.open(mode)
        try:
            for line in lines:
                isUnicode = isinstance(line, unicode)
                if linesep is not None:
                    # Strip off any existing line-end and add the
                    # specified linesep string.
                    if isUnicode:
                        if line[-2:] in (u'\r\n', u'\x0d\x85'):
                            line = line[:-2]
                        elif line[-1:] in (u'\r', u'\n',
                                           u'\x85', u'\u2028'):
                            line = line[:-1]
                    else:
                        if line[-2:] == '\r\n':
                            line = line[:-2]
                        elif line[-1:] in ('\r', '\n'):
                            line = line[:-1]
                    line += linesep
                if isUnicode:
                    if encoding is None:
                        encoding = sys.getdefaultencoding()
                    line = line.encode(encoding, errors)
                f.write(line)
        finally:
            f.close()


    # --- Methods for querying the filesystem.

    exists = os.path.exists
    isabs = os.path.isabs
    isdir = os.path.isdir
    isfile = os.path.isfile
    islink = os.path.islink
    ismount = os.path.ismount

    def type(self):
        mode = os.stat(self).st_mode
        if   stat.S_ISREG(mode):
            return self.FILE
        elif stat.S_ISDIR(mode):
            return self.DIR
        elif stat.S_ISLINK(mode):
            return self.LINK
        elif stat.S_ISCHR(mode):
            return self.CHAR
        elif stat.S_ISBLK(mode):
            return self.BLOCK
        elif stat.S_ISFIFO(mode):
            return self.PIPE
        elif stat.S_ISSOCK(mode):
            return self.SOCKET
        return None 
        
    if hasattr(os.path, 'samefile'):
        samefile = os.path.samefile

    getatime = os.path.getatime
    atime = property(
        getatime, None, None,
        """ Last access time of the file. """)

    getmtime = os.path.getmtime
    mtime = property(
        getmtime, None, None,
        """ Last-modified time of the file. """)

    if hasattr(os.path, 'getctime'):
        getctime = os.path.getctime
        ctime = property(
            getctime, None, None,
            """ Creation time of the file. """)

    getsize = os.path.getsize
    size = property(
        getsize, None, None,
        """ Size of the file, in bytes. """)

    if hasattr(os, 'access'):
        def access(self, mode):
            """ Return true if current user has access to this path.

            mode - One of the constants os.F_OK, os.R_OK, os.W_OK, os.X_OK
            """
            return os.access(self, mode)

    def stat(self):
        """ Perform a stat() system call on this path. """
        return os.stat(self)

    def lstat(self):
        """ Like path.stat(), but do not follow symbolic links. """
        return os.lstat(self)

    if hasattr(os, 'statvfs'):
        def statvfs(self):
            """ Perform a statvfs() system call on this path. """
            return os.statvfs(self)

    if hasattr(os, 'pathconf'):
        def pathconf(self, name):
            return os.pathconf(self, name)


    # --- Modifying operations on files and directories

    def utime(self, times):
        """ Set the access and modified times of this file. """
        os.utime(self, times)

    def getutime(self):
        """ Return the access and modified times in a format that can be
            passed to another path's .utime().
        """
        return self.atime, self.mtime

    def copyutimefrom(self, other):
        """ Make my access and modified times the same as the other path's.
        """
        times = other.getutime()
        self.utime(times)

    def copyutimeto(self, *others):
        """ Copy my access and modified times to the other path(s).
        """
        self.copyutimetoiter(others)

    def copyutimetoiter(self, iterpaths):
        """ Copy my access and modified times to the other path(s).
        """
        times = self.getutime()
        for other in iterpaths:
            other.utime(times)
    def chmod(self, mode):
        os.chmod(self, mode)

    if hasattr(os, 'chown'):
        def chown(self, uid, gid):
            os.chown(self, uid, gid)

    def rename(self, new):
        os.rename(self, new)

    def renames(self, new):
        os.renames(self, new)


    # --- Create/delete operations on directories

    def mkdir(self, mode=0777):
        if not self.isdir():
            os.mkdir(self, mode)

    def makedirs(self, mode=0777):
        if not self.isdir():
            os.makedirs(self, mode)

    def rmdir(self):
        if self.exists():
            os.rmdir(self)

    def removedirs(self):
        if self.exists():
            os.removedirs(self)


    # --- Modifying operations on files

    def touch(self):
        """ Set the access/modified times of this file to the current time.
        Create the file if it does not exist.
        """
        fd = os.open(self, os.O_WRONLY | os.O_CREAT, 0666)
        os.close(fd)
        os.utime(self, None)

    def remove(self):
        if self.exists():
            os.remove(self)

    def unlink(self):
        if self.exists():
            os.unlink(self)


    # --- Links

    if hasattr(os, 'link'):
        def link(self, newpath):
            """ Create a hard link at 'newpath', pointing to this file. """
            os.link(self, newpath)

    if hasattr(os, 'symlink'):
        def symlink(self, newlink):
            """ Create a symbolic link at 'newlink', pointing here. """
            os.symlink(self, newlink)

    if hasattr(os, 'readlink'):
        def readlink(self):
            """ Return the path to which this symbolic link points.

            The result may be an absolute or a relative path.
            """
            return self.__class__(os.readlink(self))

        def readlinkabs(self):
            """ Return the path to which this symbolic link points.

            The result is always an absolute path.
            """
            p = self.readlink()
            if p.isabs():
                return p
            else:
                return (self.parent / p).abspath()


    # --- High-level functions from shutil

    copyfile = shutil.copyfile
    copymode = shutil.copymode
    copystat = shutil.copystat
    copy = shutil.copy
    copy2 = shutil.copy2
    copytree = shutil.copytree
    if hasattr(shutil, 'move'):
        move = shutil.move
    rmtree = shutil.rmtree

    # --- Other high-level stuff

    def delete_dammit(self):
        """ Delete 'self', whatever it is.  Don't complain if it doesn't exist.

            Recursively deletes directories!
        """
        if   self.isfile() or self.islink():
            self.remove()
        elif self.isdir():
            self.rmtree()

    delete = delete_dammit

    def replacedir(self):
        self.delete_dammit()
        self.makedirs()

    def needsupdate(self, *others):
        """ Does 'self' need to be updated?

            Return True if 'self' does not exist or is older than any of the
            'others', which are all paths.
        """
        if not self.exists():
            return True
        mtime = self.mtime
        for other in others:
            if mtime < other.mtime:
                return True
        return False

    def chdir(self, push=False):
        """ Make 'self' the current directory.

            This may invalidate other path objects that are relative!
        """
        if push:
            cwd = os.getcwd()
            self.__class__.pushed_dirs.append(cwd)
        os.chdir(self)

    # --- Special stuff from os

    if hasattr(os, 'chroot'):
        def chroot(self):
            os.chroot(self)

    if hasattr(os, 'startfile'):
        def startfile(self):
            os.startfile(self)


emptypath = path()

# vim: sw=4 ts=4 expandtab ai
