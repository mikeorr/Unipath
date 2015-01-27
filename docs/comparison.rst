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

