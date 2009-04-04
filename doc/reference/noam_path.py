#format PYTHON
# -*- coding: iso-8859-1 -*-
""" path.py - An object representing a path to a file or a directory.

Based on the path module by Jason Orendorff
(http://www.jorendorff.com/articles/python/path)

Written by Noam Raphael to show the idea of using a tuple instead of
a string, and to reduce the number of methods.

Currently only implements posix and nt paths - more can be added.

"""

import os
import stat
import itertools
import fnmatch
import re
import string

class StatWrapper(object):
    """ A wrapper around stat_result objects which gives additional properties.
    
    This object is a wrapper around a stat_result object. It allows access
    to all the original object's attributes, and adds a few convinient
    properties, by using the stat module.
    
    This object should have been a subclass posix.stat_result - it simply
    isn't possible currently. This functionality may also be integrated into
    the original type.
    """
    
    __slots__ = ['_stat']
    
    def __init__(self, stat):
        self._stat = stat
        
    def __getattribute__(self, attr, *default):
        try:
            return object.__getattribute__(self, attr, *default)
        except AttributeError:
            return getattr(self._stat, attr, *default)

    # Mode properties
    
    @property
    def isdir(self):
        return stat.S_ISDIR(self.st_mode)
    @property
    def isfile(self):
        return stat.S_ISREG(self.st_mode)
    @property
    def islink(self):
        return stat.S_ISLNK(self.st_mode)
    
    # Easier names properties

    @property
    def size(self):
        return self.st_size
    @property
    def mtime(self):
        return self.st_mtime
    @property
    def atime(self):
        return self.st_atime
    @property
    def ctime(self):
        return self.st_ctime


class BasePath(tuple):
    """ The base, abstract, path type.
    
    The OS-specific path types inherit from it.
    """

    # ----------------------------------------------------------------
    # We start with methods which don't use system calls - they just
    # manipulate paths.

    class _BaseRoot(object):
        """ Represents a start location for a path.
        
        A Root is an object which may be the first element of a path tuple,
        and represents from where to start the path.
        
        On posix, there's only one: ROOT (singleton).
        On nt, there are a few:
          CURROOT - the root of the current drive (singleton)
          Drive(letter) - the root of a specific drive
          UnrootedDrive(letter) - the current working directory on a specific
                                  drive
          UNCRoot(host, mountpoint) - a UNC mount point

        The class for each OS has its own root classes, which should inherit
        from _OSBaseRoot.

        str(root) should return the string name of the root. The string should
        identify the root: two root elements with the same string should have
        the same meaning. To allow meaningful sorting of path objects, root
        objects can be compared to strings and other root objects. They are
        smaller than all strings, and are compared with other root objects
        according to their string name.

        Every Root object should contain the "isabs" attribute, which is True
        if changes in the current working directory won't change the meaning
        of the root and False otherwise. (CURROOT and UnrootedDrive aren't
        absolute)
        If isabs is True, it should also implement the abspath() method, which
        should return an absolute path object, equivalent to the root when the
        call was made.
        """
        isabs = None

        def abspath(self):
            if self.abspath:
                raise NotImplementedError, 'This root is already absolute'
            else:
                raise NotImplementedError, 'abspath is abstract'

        def __str__(self):
            raise NotImplementedError, '__str__ is abstract'

        def __cmp__(self, other):
            if isinstance(other, str):
                return -1
            elif isinstance(other, BasePath._BaseRoot):
                return cmp(str(self), str(other))
            else:
                raise TypeError, 'Comparison not defined'

        def __hash__(self):
            # This allows path objects to be hashable
            return hash(str(self))

    # _OSBaseRoot should be the base of the OS-specific root classes, which
    # should inherit from _BaseRoot
    _OSBaseRoot = None

    # These string constants should be filled by subclasses - they are real
    # directory names
    curdir = None
    pardir = None

    # These string constants are used by default implementations of methods,
    # but are not part of the interface - the whole idea is for the interface
    # to hide those details.
    _sep = None
    _altsep = None

    @staticmethod
    def _parse_str(pathstr):
        # Concrete path classes should implement _parse_str to get a path
        # string and return an iterable over path elements.
        raise NotImplementedError, '_parse_str is abstract'

    @staticmethod
    def normcasestr(string):
        """ Normalize the case of one path element.
        
        This default implementation returns string unchanged. On
        case-insensitive platforms, it returns the normalized string.
        """
        return string

    # We make this method a property, to show that it doesn't use any
    # system calls.
    # Case-sensitive subclasses can redefine it to return self.
    @property
    def normcase(self):
        """ Return an equivalent path with case-normalized elements. """
        if self.isrel:
            return self.__class__(self.normcasestr(element)
                                  for element in self)
        else:
            def gen():
                it = iter(self)
                yield it.next()
                for element in it:
                    yield self.normcasestr(element)
            return self.__class__(gen())

    @classmethod
    def _normalize_elements(cls, elements):
        # This method gets an iterable over path elements.
        # It should return an iterator over normalized path elements -
        # that is, curdir elements should be ignored.
        
        for i, element in enumerate(elements):
            if isinstance(element, str):
                if element != cls.curdir:
                    if (not element or
                        cls._sep in element or
                        (cls._altsep and cls._altsep in element)):
                        # Those elements will cause path(str(x)) != x
                        raise ValueError, "Element %r is invalid" % element
                    yield element
            elif i == 0 and isinstance(element, cls._OSBaseRoot):
                yield element
            else:
                raise TypeError, "Element %r is of a wrong type" % element

    def __new__(cls, arg=None):
        """ Create a new path object.
        
        If arg isn't given, an empty path, which represents the current
        working directory, is returned.
        If arg is a string, it is parsed into a logical path.
        If arg is an iterable over path elements, a new path is created from
        them.
        """
        if arg is None:
            return tuple.__new__(cls)
        elif type(arg) is cls:
            return arg
        elif isinstance(arg, str):
            return tuple.__new__(cls, cls._parse_str(arg))
        else:
            return tuple.__new__(cls, cls._normalize_elements(arg))

    def __init__(self, arg=None):
        # Since paths are immutable, we can cache the string representation
        self._cached_str = None

    def _build_str(self):
        # Return a string representation of self.
        # 
        # This is a default implementation, which may be overriden by
        # subclasses (form example, MacPath)
        if not self:
            return self.curdir
        elif isinstance(self[0], self._OSBaseRoot):
            return str(self[0]) + self._sep.join(self[1:])
        else:
            return self._sep.join(self)

    def __str__(self):
        """ Return a string representation of self. """
        if self._cached_str is None:
            self._cached_str = self._build_str()
        return self._cached_str

    def __repr__(self):
        # We want path, not the real class name.
        return 'path(%r)' % str(self)

    @property
    def isabs(self):
        """ Return whether this path represent an absolute path.

        An absolute path is a path whose meaning doesn't change when the
        the current working directory changes.
        
        (Note that this is not the same as "not self.isrelative")
        """
        return len(self) > 0 and \
               isinstance(self[0], self._OSBaseRoot) and \
               self[0].isabs

    @property
    def isrel(self):
        """ Return whether this path represents a relative path.

        A relative path is a path without a root element, so it can be
        concatenated to other paths.

        (Note that this is not the same as "not self.isabs")
        """
        return len(self) == 0 or \
               not isinstance(self[0], self._OSBaseRoot)

    # Wrap a few tuple methods to return path objects

    def __add__(self, other):
        other = self.__class__(other)
        if not other.isrel:
            raise ValueError, "Right operand should be a relative path"
        return self.__class__(itertools.chain(self, other))

    def __radd__(self, other):
        if not self.isrel:
            raise ValueError, "Right operand should be a relative path"
        other = self.__class__(other)
        return self.__class__(itertools.chain(other, self))

    def __getslice__(self, *args):
        return self.__class__(tuple.__getslice__(self, *args))

    def __mul__(self, *args):
        if not self.isrel:
            raise ValueError, "Only relative paths can be multiplied"
        return self.__class__(tuple.__mul__(self, *args))

    def __rmul__(self, *args):
        if not self.isrel:
            raise ValueError, "Only relative paths can be multiplied"
        return self.__class__(tuple.__rmul__(self, *args))

    def __eq__(self, other):
        return tuple.__eq__(self, self.__class__(other))
    def __ge__(self, other):
        return tuple.__ge__(self, self.__class__(other))
    def __gt__(self, other):
        return tuple.__gt__(self, self.__class__(other))
    def __le__(self, other):
        return tuple.__le__(self, self.__class__(other))
    def __lt__(self, other):
        return tuple.__lt__(self, self.__class__(other))
    def __ne__(self, other):
        return tuple.__ne__(self, self.__class__(other))
        

    # ----------------------------------------------------------------
    # Now come the methods which use system calls.

    # --- Path transformation which use system calls

    @classmethod
    def cwd(cls):
        return cls(os.getcwd())

    def chdir(self):
        return os.chdir(str(self))

    def abspath(self):
        if not self:
            return self.cwd()
        if isinstance(self[0], self._OSBaseRoot):
            if self[0].isabs:
                return self
            else:
                return self[0].abspath() + self[1:]
        else:
            return self.cwd() + self

    def realpath(self):
        return self.__class__(os.path.realpath(str(self)))

    def relpathto(self, dst):
        """ Return a relative path from self to dest.

        This method examines self.realpath() and dest.realpath(). If
        they have the same root element, a path in the form
        path([path.pardir, path.pardir, ..., dir1, dir2, ...])
        is returned. If they have different root elements,
        dest.realpath() is returned.
        """
        src = self.realpath()
        dst = self.__class__(dst).realpath()

        if src[0] == dst[0]:
            # They have the same root
            
            # find the length of the equal prefix
            i = 1
            while i < len(src) and i < len(dst) and \
                  self.normcasestr(src[i]) == self.normcasestr(dst[i]):
                i += 1

            return [self.pardir] * (len(src) - i) + dst[i:]

        else:
            # They don't have the same root
            return dst
            

    

    # --- Expand

    def expanduser(self):
        return path(os.path.expanduser(str(self)))

    def expandvars(self):
        return path(os.path.expandvars(str(self)))
    

    # --- Info about the path

    def stat(self):
        return StatWrapper(os.stat(str(self)))
    
    def exists(self):
        try:
            self.stat()
        except OSError:
            return False
        else:
            return True

    def isdir(self):
        try:
            return self.stat().isdir
        except OSError:
            return False

    def isfile(self):
        try:
            return self.stat().isfile
        except OSError:
            return False
        
    def lstat(self):
        return StatWrapper(os.lstat(str(self)))

    def lexists(self):
        try:
            self.lstat()
        except OSError:
            return False
        else:
            return True

    def lisdir(self):
        try:
            return self.stat().lisdir
        except OSError:
            return False

    def lisfile(self):
        try:
            return self.stat().lisfile
        except OSError:
            return False

    def islink(self):
        try:
            return self.lstat().islink
        except OSError:
            return False
        
    def ismount(self):
        return os.path.ismount(str(self))

    def access(self, mode):
        """ Return true if current user has access to this path.

        mode - One of the constants os.F_OK, os.R_OK, os.W_OK, os.X_OK
        """
        return os.access(str(self), mode)

    # Additional methods in subclasses:
    # statvfs (PosixPath)
    # pathconf (PosixPath, XXX MacPath)
    # samefile (PosixPath, XXX MacPath)


    # --- Modifying operations on files and directories

    def utime(self, times):
        """ Set the access and modified times of this file. """
        os.utime(str(self), times)

    def chmod(self, mode):
        os.chmod(str(self), mode)

    def rename(self, new):
        os.rename(str(self), str(new))

    # Additional methods in subclasses:
    # chown (PosixPath, XXX MacPath)
    # lchown (PosixPath, XXX MacPath)


    # --- Create/delete operations on directories

    def mkdir(self, mode=0777):
        os.mkdir(str(self), mode)

    def makedirs(self, mode=0777):
        os.makedirs(str(self), mode)

    def rmdir(self):
        os.rmdir(str(self))

    def removedirs(self, base=None):
        """ Remove empty directories recursively.
        
        If the directory is empty, remove it. If the parent directory becomes
        empty, remove it too. Continue until a directory can't be removed,
        because it's not empty or for other reasons.
        If base is given, it should be a prefix of self. base won't be removed
        even if it becomes empty.
        Note: only directories explicitly listed in the path will be removed.
        This means that if self is a relative path, predecesors of the
        current working directory won't be removed.
        """
        if not self.stat().isdir:
            raise OSError, 'removedirs only works on directories.'
        base = self.__class__(base)
        if base:
            if not self[:len(base)] == base:
                raise ValueError, 'base should be a prefix of self.'
            stopat = len(base)
        else:
            stopat = 0
        for i in xrange(len(self), stopat, -1):
            try:
                self[:i].rmdir()
            except OSError:
                break

    def rmtree(self, *args):
        return shutil.rmtree(str(self), *args)


    # --- Modifying operations on files

    def touch(self):
        """ Set the access/modified times of this file to the current time.
        Create the file if it does not exist.
        """
        fd = os.open(str(self), os.O_WRONLY | os.O_CREAT, 0666)
        os.close(fd)
        os.utime(str(self), None)

    def remove(self):
        os.remove(str(self))

    def copy(self, dst, copystat=False):
        """ Copy file from self to dst.

        If copystat is False, copy data and mode bits ("cp self dst").
        If copystat is True, copy data and all stat info ("cp -p self dst").

        The destination may be a directory. If so, a file with the same base
        name as self will be created in that directory.
        """
        dst = self.__class__(dst)
        if dst.stat().isdir:
            dst += self[-1]
        shutil.copyfile(str(self), str(dst))
        if copystat:
            shutil.copystat(str(self), str(dst))
        else:
            shutil.copymode(str(self), str(dst))

    def move(self, dst):
        dst = self.__class__(dst)
        return shutil.move(str(self), str(dst))
        

    # --- Links

    # In subclasses:
    # link (PosixPath, XXX MacPath)
    # writelink (PosixPath) - what about MacPath?
    # readlink (PosixPath, XXX MacPath)
    # readlinkpath (PosixPath, XXXMacPath)


    # --- Extra

    # In subclasses:
    # mkfifo (PosixPath, XXX MacPath)
    # mknod (PosixPath, XXX MacPath)
    # chroot (PosixPath, XXX MacPath)
    #
    # startfile (NTPath)


    # --- Globbing

    # If the OS supports it, _id should be a function that gets a stat object
    # and returns a unique id of a file.
    # It the OS doesn't support it, it should be None.
    _id = None

    @staticmethod
    def _match_element(comp_element, element):
        # Does a filename match a compiled pattern element?
        # The filename should be normcased.
        if comp_element is None:
            return True
        elif isinstance(comp_element, str):
            return comp_element == element
        else:
            return comp_element.match(element)

    def _glob(cls, pth, comp_pattern, topdown, onlydirs, onlyfiles,
              positions, on_path, stat):
        """ The recursive function used by glob.

        This version treats symbolic links as files. Broken symlinks won't be
        listed.

        pth is a dir in which we search.
        
        comp_pattern is the compiled pattern. It's a sequence which should
        consist of three kinds of elements:
        * None - matches any number of subdirectories, including 0.
        * a string - a normalized name, when exactly one name can be matched.
        * a regexp - for testing if normalized names match.

        positions is a sequence of positions on comp_pattern that children of
        path may match. On the first call, if will be [0].

        on_path is a set of inode identifiers on path, or None if circles
        shouldn't be checked.

        stat is the appropriate stat function - cls.stat or cls.lstat.
        """

        if len(positions) == 1 and isinstance(comp_pattern[positions[0]], str):
            # We don't have to listdir if exactly one file name can match.
            # Since we always stat the files, it's ok if the file doesn't exist.
            listdir = [comp_pattern[positions[0]]]
        else:
            listdir = os.listdir(str(pth))
            listdir.sort()

        for subfile in listdir:
            newpth = pth + subfile
            # We don't strictly need to stat a file if we don't follow symlinks
            # AND positions == [len(comp_pattern)-1] AND
            # not isinstance(comp_pattern[-1], str), but do me a favour...
            try:
                st = stat(newpth)
            except OSError:
                continue
            newpositions = []
            subfilenorm = cls.normcasestr(subfile)
            
            if topdown:
                # If not topdown, it happens after we handle subdirs
                if positions[-1] == len(comp_pattern) - 1:
                    if cls._match_element(comp_pattern[-1], subfilenorm):
                        if not ((onlydirs and not st.isdir) or
                                (onlyfiles and not st.isfile)):
                            yield newpth

            for pos in reversed(positions):
                if st.isdir:
                    comp_element = comp_pattern[pos]
                    if pos + 1 < len(comp_pattern):
                        if cls._match_element(comp_element, subfilenorm):
                            newpositions.append(pos + 1)
                            if comp_pattern[pos + 1] is None:
                                # We should stop at '..'
                                break
                    if comp_element is None:
                        newpositions.append(pos)
                        # We don't have to break - there are not supposed
                        # to be any positions before '..'.

            if newpositions:
                newpositions.reverse()

                if on_path is not None:
                    newpath_id = cls._id(st)
                    if newpath_id in on_path:
                        raise OSError, "Circular path encountered"
                    on_path.add(newpath_id)

                for x in cls._glob(newpth,
                                   comp_pattern, topdown, onlydirs, onlyfiles,
                                   newpositions, on_path, stat):
                    yield x

                if on_path is not None:
                    on_path.remove(newpath_id)

            if not topdown:
                # If topdown, it happens after we handle subdirs
                if positions[-1] == len(comp_pattern) - 1:
                    if cls._match_element(comp_pattern[-1], subfilenorm):
                        if not ((onlydirs and not st.isdir) or
                                (onlyfiles and not st.isfile)):
                            yield newpth

    _magic_check = re.compile('[*?[]')

    @classmethod
    def _has_magic(cls, s):
        return cls._magic_check.search(s) is not None

    _cache = {}

    @classmethod
    def _compile_pattern(cls, pattern):
        # Get a pattern, return the list of compiled pattern elements
        # and the list of initial positions.
        pattern = cls(pattern)
        if not pattern.isrel:
            raise ValueError, "pattern should be a relative path."

        comp_pattern = []
        last_was_none = False
        for element in pattern:
            element = cls.normcasestr(element)
            if element == '**':
                if not last_was_none:
                    comp_pattern.append(None)
            else:
                last_was_none = False
                if not cls._has_magic(element):
                    comp_pattern.append(element)
                else:
                    try:
                        r = cls._cache[element]
                    except KeyError:
                        r = re.compile(fnmatch.translate(element))
                        cls._cache[element] = r
                    comp_pattern.append(r)

        if comp_pattern[0] is None and len(comp_pattern) > 1:
            positions = [0, 1]
        else:
            positions = [0]

        return comp_pattern, positions

    def match(self, pattern):
        """ Return whether self matches the given pattern.

        pattern has the same meaning as in the glob method.
        self should be relative.

        This method doesn't use any system calls.
        """
        if not self.isrel:
            raise ValueError, "self must be a relative path"
        comp_pattern, positions = self._compile_pattern(pattern)

        for element in self.normcase:
            newpositions = []
            for pos in reversed(positions):
                if pos == len(comp_pattern):
                    # We matched the pattern but the path isn't finished -
                    # too bad
                    continue
                comp_element = comp_pattern[pos]
                if self._match_element(comp_element, element):
                    newpositions.append(pos + 1)
                if comp_element is None:
                    newpositions.append(pos)
                    # No need to continue after a '**'
                    break
            newpositions.reverse()
            positions = newpositions
            if not positions:
                # No point in carrying on
                break

        return (len(comp_pattern) in positions)

    def glob(self, pattern='*', topdown=True, onlydirs=False, onlyfiles=False):
        """ Return an iterator over all files in self matching pattern.

        pattern should be a relative path, which may include wildcards.
        In addition to the regular shell wildcards, you can use '**', which
        matches any number of directories, including 0.

        If topdown is True (the default), a directory is yielded before its
        descendents. If it's False, a directory is yielded after its
        descendents.

        If onlydirs is True, only directories will be yielded. If onlyfiles
        is True, only regular files will be yielded.

        This method treats symbolic links as regular files. Broken symlinks
        won't be yielded.
        """

        if onlydirs and onlyfiles:
            raise ValueError, \
                  "Only one of onlydirs and onlyfiles can be specified."

        comp_pattern, positions = self._compile_pattern(pattern)

        if self._id is not None and None in comp_pattern:
            on_path = set([self._id(self.stat())])
        else:
            on_path = None
            
        for x in self._glob(self, comp_pattern, topdown, onlydirs, onlyfiles,
                            positions, on_path, self.__class__.stat):
            yield x
        
    def lglob(self, pattern='*', topdown=True, onlydirs=False, onlyfiles=False):
        """ Return an iterator over all files in self matching pattern.

        pattern should be a relative path, which may include wildcards.
        In addition to the regular shell wildcards, you can use '**', which
        matches any number of directories, including 0.

        If topdown is True (the default), a directory is yielded before its
        descendents. If it's False, a directory is yielded after its
        descendents.

        If onlydirs is True, only directories will be yielded. If onlyfiles
        is True, only regular files will be yielded.

        This method treats symbolic links as special files - they won't be
        followed, and they will be yielded even if they're broken.
        """

        if onlydirs and onlyfiles:
            raise ValueError, \
                  "Only one of onlydirs and onlyfiles can be specified."

        comp_pattern, positions = self._compile_pattern(pattern)
            
        for x in self._glob(self, comp_pattern, topdown, onlydirs, onlyfiles,
                            positions, None, self.__class__.lstat):
            yield x


class PosixPath(BasePath):
    """ Represents POSIX paths. """
    
    class _PosixRoot(BasePath._BaseRoot):
        """ Represents the filesystem root (/).
        
        There's only one root on posix systems, so this is a singleton.
        """
        instance = None
        def __new__(cls):
            if cls.instance is None:
                instance = object.__new__(cls)
                cls.instance = instance
            return cls.instance
        
        def __str__(self):
            return '/'

        def __repr__(self):
            return 'path.ROOT'

        isabs = True

    _OSBaseRoot = _PosixRoot

    ROOT = _PosixRoot()

    # Public constants
    curdir = '.'
    pardir = '..'

    # Private constants
    _sep = '/'
    _altsep = None

    @classmethod
    def _parse_str(cls, pathstr):
        # get a path string and return an iterable over path elements.
        if pathstr.startswith('/'):
            if pathstr.startswith('//') and not pathstr.startswith('///'):
                # Two initial slashes have application-specific meaning
                # in POSIX, and it's not supported currently.
                raise NotImplementedError, \
                      "Paths with two leading slashes aren't supported."
            yield cls.ROOT
        for element in pathstr.split('/'):
            if element == '' or element == cls.curdir:
                continue
            # '..' aren't specially treated, since popping the last
            # element isn't correct if the last element was a symbolic
            # link.
            yield element


    # POSIX-specific methods
    

    # --- Info about the path

    def statvfs(self):
        """ Perform a statvfs() system call on this path. """
        return os.statvfs(str(self))

    def pathconf(self, name):
        return os.pathconf(str(self), name)

    def samefile(self, other):
        other = self.__class__(other)
        s1 = self.stat()
        s2 = other.stat()
        return s1.st_ino == s2.st_ino and \
               s1.st_dev == s2.st_dev


    # --- Modifying operations on files and directories

    def chown(self, uid=None, gid=None):
        if uid is None:
            uid = -1
        if gid is None:
            gid = -1
        return os.chown(str(self), uid, gid)
    
    def lchown(self, uid=None, gid=None):
        if uid is None:
            uid = -1
        if gid is None:
            gid = -1
        return os.lchown(str(self), uid, gid)


    # --- Links

    def link(self, newpath):
        """ Create a hard link at 'newpath', pointing to this file. """
        os.link(str(self), str(newpath))

    def writelink(self, src):
        """ Create a symbolic link at self, pointing to src.

        src may be any string. Note that if it's a relative path, it
        will be interpreted relative to self, not relative to the current
        working directory.
        """
        os.symlink(str(src), str(self))

    def readlink(self):
        """ Return the path to which this symbolic link points.

        The result is a string, which may be an absolute path, a
        relative path (which should be interpreted relative to self[:-1]),
        or any arbitrary string.
        """
        return os.readlink(str(self))

    def readlinkpath(self):
        """ Return the path to which this symbolic link points. """
        linkpath = self.__class__(self.readlink())
        if linkpath.isrel:
            return self + linkpath
        else:
            return linkpath


    # --- Extra

    def mkfifo(self, *args):
        return os.mkfifo(str(self), *args)

    def mknod(self, *args):
        return os.mknod(str(self), *args)

    def chroot(self):
        return os.chroot(str(self))


    # --- Globbing

    @staticmethod
    def _id(stat):
        return (stat.st_ino, stat.st_dev)


class NTPath(BasePath):
    """ Represents paths on Windows operating systems. """

    class _NTBaseRoot(BasePath._BaseRoot):
        """ The base class of all Windows root classes. """
        pass

    _OSBaseRoot = _NTBaseRoot

    class _CurRootType(_NTBaseRoot):
        """ Represents the root of the current working drive.
        
        This class is a singleton. It represents the root of the current
        working drive - paths starting with '\'.
        """
        instance = None
        def __new__(cls):
            if cls.instance is None:
                instance = object.__new__(cls)
                cls.instance = instance
            return cls.instance
        
        def __str__(self):
            return '\\'

        def __repr__(self):
            return 'path.CURROOT'

        isabs = False

        def abspath(self):
            from nt import _getfullpathname
            return NTPath(_getfullpathname(str(self)))

    CURROOT = _CurRootType()

    class Drive(_NTBaseRoot):
        """ Represents the root of a specific drive. """
        def __init__(self, letter):
            # Drive letter is normalized - we don't lose any information
            if len(letter) != 1 or letter not in string.letters:
                raise ValueError, 'Should get one letter'
            self._letter = letter.lower()

        @property
        def letter(self):
            # We use a property because we want the object to be immutable.
            return self._letter

        def __str__(self):
            return '%s:\\' % self.letter

        def __repr__(self):
            return 'path.Drive(%r)' % self.letter

        isabs = True

    class UnrootedDrive(_NTBaseRoot):
        """ Represents the current working directory on a specific drive. """
        def __init__(self, letter):
            # Drive letter is normalized - we don't lose any information
            if len(letter) != 1 or letter not in string.letters:
                raise ValueError, 'Should get one letter'
            self._letter = letter.lower()

        @property
        def letter(self):
            # We use a property because we want the object to be immutable.
            return self._letter

        def __str__(self):
            return '%s:' % self.letter

        def __repr__(self):
            return 'path.UnrootedDrive(%r)' % self.letter

        isabs = False

        def abspath(self):
            from nt import _getfullpathname
            return NTPath(_getfullpathname(str(self)))

    class UNCRoot(_NTBaseRoot):
        """ Represents a UNC mount point. """
        def __init__(self, host, mountpoint):
            # Host and mountpoint are normalized - we don't lose any information
            self._host = host.lower()
            self._mountpoint = mountpoint.lower()

        @property
        def host(self):
            # We use a property because we want the object to be immutable.
            return self._host

        @property
        def mountpoint(self):
            # We use a property because we want the object to be immutable.
            return self._mountpoint

        def __str__(self):
            return '\\\\%s\\%s\\' % (self.host, self.mountpoint)

        def __repr__(self):
            return 'path.UNCRoot(%r, %r)' % (self.host, self.mountpoint)

        isabs = True
            
            
    # Public constants
    curdir = '.'
    pardir = '..'

    # Private constants
    _sep = '\\'
    _altsep = '/'

    @staticmethod
    def normcasestr(string):
        """ Normalize the case of one path element.
        
        On Windows, this returns string.lower()
        """
        return string.lower()

    @classmethod
    def _parse_str(cls, pathstr):
        # get a path string and return an iterable over path elements.

        # First, replace all backslashes with slashes.
        # I know that it should have been the other way round, but I can't
        # stand all those escapes.
        
        pathstr = pathstr.replace('\\', '/')

        # Handle the root element
        
        if pathstr.startswith('/'):
            if pathstr.startswith('//'):
                # UNC Path
                if pathstr.startswith('///'):
                    raise ValueError, \
                          "Paths can't start with more than two slashes"
                index = pathstr.find('/', 2)
                if index == -1:
                    raise ValueError, \
                          "UNC host name should end with a slash"
                index2 = index+1
                while pathstr[index2:index2+1] == '/':
                    index2 += 1
                if index2 == len(pathstr):
                    raise ValueError, \
                          "UNC mount point is empty"
                index3 = pathstr.find('/', index2)
                if index3 == -1:
                    index3 = len(pathstr)
                yield cls.UNCRoot(pathstr[2:index], pathstr[index2:index3])
                pathstr = pathstr[index3:]
            else:
                # CURROOT
                yield cls.CURROOT
        else:
            if pathstr[1:2] == ':':
                if pathstr[2:3] == '/':
                    # Rooted drive
                    yield cls.Drive(pathstr[0])
                    pathstr = pathstr[3:]
                else:
                    # Unrooted drive
                    yield cls.UnrootedDrive(pathstr[0])
                    pathstr = pathstr[2:]

        # Handle all other elements
        
        for element in pathstr.split('/'):
            if element == '' or element == cls.curdir:
                continue
            # We don't treat pardir specially, since in the presence of
            # links there's nothing to do about them.
            # Windows doesn't have links, but why not keep path handling
            # similiar?
            yield element


    # NT-specific methods

    # --- Extra

    def startfile(self):
        return os.startfile(str(self))

if os.name == 'posix':
    path = PosixPath
elif os.name == 'nt':
    path = NTPath
else:
    raise NotImplementedError, \
          "The path object is currently not implemented for OS %r" % os.name
