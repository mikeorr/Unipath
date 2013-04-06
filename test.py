#!/usr/bin/env python
"""Unit tests for unipath.py

Environment variables:
    DUMP : List the contents of test direcories after each test.
    NO_CLEANUP : Don't delete test directories.
(These are not command-line args due to the difficulty of merging my args
with unittest's.)

IMPORTANT: Tests may not assume what the current directory is because the tests
may have been started from anywhere, and some tests chdir to the temprorary
test directory which is then deleted.
"""
from __future__ import print_function

import ntpath
import os
import posixpath
import tempfile
import time
import sys

import pytest

from unipath import *
from unipath.errors import *
from unipath.tools import dict2dir, dump_path

AbstractPath.auto_norm = False

class PosixPath(AbstractPath):
    pathlib = posixpath


class NTPath(AbstractPath):
    pathlib = ntpath

# Global flags
cleanup = not bool(os.environ.get("NO_CLEANUP"))
dump = bool(os.environ.get("DUMP"))
        

class TestPathConstructor(object):
    def test_posix(self):
        assert str(PosixPath()) == posixpath.curdir
        assert str(PosixPath("foo/bar.py")) == "foo/bar.py"
        assert str(PosixPath("foo", "bar.py")) == "foo/bar.py"
        assert str(PosixPath("foo", "bar", "baz.py")) == "foo/bar/baz.py"
        assert str(PosixPath("foo", PosixPath("bar", "baz.py"))) == "foo/bar/baz.py"
        assert str(PosixPath("foo", ["", "bar", "baz.py"])) == "foo/bar/baz.py"
        assert str(PosixPath("")) == ""
        assert str(PosixPath()) == "."
        assert str(PosixPath("foo", 1, "bar")) == "foo/1/bar"

    def test_nt(self):
        assert str(NTPath()) == ntpath.curdir
        assert str(NTPath(r"foo\bar.py")) == r"foo\bar.py"
        assert str(NTPath("foo", "bar.py")), r"foo\bar.py"
        assert str(NTPath("foo", "bar", "baz.py")) == r"foo\bar\baz.py"
        assert str(NTPath("foo", NTPath("bar", "baz.py"))) == r"foo\bar\baz.py"
        assert str(NTPath("foo", ["", "bar", "baz.py"])) == r"foo\bar\baz.py"
        assert str(PosixPath("")) == ""
        assert str(NTPath()) == "."
        assert str(NTPath("foo", 1, "bar")) == r"foo\1\bar"

    def test_int_arg(self):
        assert str(PosixPath("a", 1)) == "a/1"


class TestNorm(object):
    def test_posix(self):
        assert PosixPath("a//b/../c").norm() == "a/c"
        assert PosixPath("a/./b").norm() == "a/b"
        assert PosixPath("a/./b", norm=True) == "a/b"
        assert PosixPath("a/./b", norm=False) == "a/./b"

        class AutoNormPath(PosixPath):
            auto_norm = True
        assert AutoNormPath("a/./b") == "a/b"
        assert AutoNormPath("a/./b", norm=True) == "a/b"
        assert AutoNormPath("a/./b", norm=False) == "a/./b"

    def test_nt(self):
        assert NTPath(r"a\\b\..\c").norm() == r"a\c"
        assert NTPath(r"a\.\b").norm() == r"a\b"
        assert NTPath("a\\.\\b", norm=True) == "a\\b"
        assert NTPath("a\\.\\b", norm=False) == "a\\.\\b"

        class AutoNormPath(NTPath):
            auto_norm = True
        assert AutoNormPath("a\\.\\b") == "a\\b"
        assert AutoNormPath("a\\.\\b", norm=True) == "a\\b"
        assert AutoNormPath("a\\.\\b", norm=False) == "a\\.\\b"


class TestAbstractPath(object):
    def test_repr(self):
        assert repr(Path("la_la_la")) == "Path('la_la_la')"
        assert repr(NTPath("la_la_la")) == "NTPath('la_la_la')"

    # Not testing expand_user, expand_vars, or expand: too dependent on the
    # OS environment.

    def test_properties(self):
        p = PosixPath("/first/second/third.jpg")
        assert p.parent == "/first/second"
        assert p.name == "third.jpg"
        assert p.ext == ".jpg"
        assert p.stem == "third"

    def test_properties2(self):
        # Usage sample in README is based on this.
        p = PosixPath("/usr/lib/python2.5/gopherlib.py")
        assert p.parent == Path("/usr/lib/python2.5")
        assert p.name == Path("gopherlib.py")
        assert p.ext == ".py"
        assert p.stem == Path("gopherlib")
        q = PosixPath(p.parent, p.stem + p.ext)
        assert q == p

    def test_split_root(self):
        assert PosixPath("foo/bar.py").split_root() == ("", "foo/bar.py")
        assert PosixPath("/foo/bar.py").split_root() == ("/", "foo/bar.py")
        assert NTPath("foo\\bar.py").split_root() == ("", "foo\\bar.py")
        assert NTPath("\\foo\\bar.py").split_root() == ("\\", "foo\\bar.py")
        assert NTPath("C:\\foo\\bar.py").split_root() == ("C:\\", "foo\\bar.py")
        assert NTPath("C:foo\\bar.py").split_root() == ("C:", "foo\\bar.py")
        assert NTPath("\\\\share\\base\\foo\\bar.py").split_root() == ("\\\\share\\base\\", "foo\\bar.py")

    def test_split_root_vs_isabsolute(self):
        assert not PosixPath("a/b/c").isabsolute()
        assert not PosixPath("a/b/c").split_root()[0]
        assert PosixPath("/a/b/c").isabsolute()
        assert PosixPath("/a/b/c").split_root()[0]
        assert not NTPath("a\\b\\c").isabsolute()
        assert not NTPath("a\\b\\c").split_root()[0]
        assert NTPath("\\a\\b\\c").isabsolute()
        assert NTPath("\\a\\b\\c").split_root()[0]
        assert NTPath("C:\\a\\b\\c").isabsolute()
        assert NTPath("C:\\a\\b\\c").split_root()[0]
        assert NTPath("C:a\\b\\c").isabsolute()
        assert NTPath("C:a\\b\\c").split_root()[0]
        assert NTPath("\\\\share\\b\\c").isabsolute()
        assert NTPath("\\\\share\\b\\c").split_root()[0]

    def test_components(self):
        P = PosixPath
        assert P("a").components() == [P(""), P("a")]
        assert P("a/b/c").components() == [P(""), P("a"), P("b"), P("c")]
        assert P("/a/b/c").components() == [P("/"), P("a"), P("b"), P("c")]
        P = NTPath
        assert P("a\\b\\c").components() == [P(""), P("a"), P("b"), P("c")]
        assert P("\\a\\b\\c").components() == [P("\\"), P("a"), P("b"), P("c")]
        assert P("C:\\a\\b\\c").components() == [P("C:\\"), P("a"), P("b"), P("c")]
        assert P("C:a\\b\\c").components() == [P("C:"), P("a"), P("b"), P("c")]
        assert P("\\\\share\\b\\c").components() == [P("\\\\share\\b\\"), P("c")]

    def test_child(self):
        PosixPath("foo/bar").child("baz")
        with pytest.raises(UnsafePathError):
            PosixPath("foo/bar").child("baz/fred")
            PosixPath("foo/bar").child("..", "baz")
            PosixPath("foo/bar").child(".", "baz")


class TestStringMethods(object):
    def test_add(self):
        P = PosixPath
        assert P("a") + P("b") == P("ab")
        assert P("a") + "b" == P("ab")
        assert "a" + P("b") == P("ab")


class FilesystemTest(object):
    TEST_HIERARCHY = {
        "a_file":  "Nothing important.",
        "animals": {
            "elephant":  "large",
            "gonzo":  "unique",
            "mouse":  "small"},
        "images": {
            "image1.gif": "",
            "image2.jpg": "",
            "image3.png": ""},
        "swedish": {
            "chef": {
                "bork": {
                    "bork": "bork!"}}},
    }

    def setup_method(self, method):
        self.d = d = Path(tempfile.mkdtemp())
        dict2dir(d, self.TEST_HIERARCHY)
        self.a_file = Path(d, "a_file")
        self.animals = Path(d, "animals")
        self.images = Path(d, "images")
        self.chef = Path(d, "swedish", "chef", "bork", "bork")
        if hasattr(self.d, "write_link"):
            self.link_to_chef_file = Path(d, "link_to_chef_file")
            self.link_to_chef_file.write_link(self.chef)
            self.link_to_images_dir = Path(d, "link_to_images_dir")
            self.link_to_images_dir.write_link(self.images)
            self.dead_link = self.d.child("dead_link")
            self.dead_link.write_link("nowhere")
        self.missing = Path(d, "MISSING")
        self.d.chdir()

    def teardown_method(self, method):
        d = self.d
        d.parent.chdir()  # Always need a valid curdir to avoid OSErrors.
        if dump:
            dump_path(d)
        if cleanup:
            d.rmtree()
            if d.exists():
                raise AssertionError("unable to delete temp dir %s" % d)
        else:
            print("Not deleting test directory", d)


class TestCalculatingPaths(FilesystemTest):
    def test_inheritance(self):
        assert Path.cwd().name   # Can we access the property?

    def test_cwd(self):
        assert str(Path.cwd()) == os.getcwd()

    def test_chdir_absolute_relative(self):
        save_dir = Path.cwd()
        self.d.chdir()
        assert Path.cwd() == self.d
        assert Path("swedish").absolute() == Path(self.d, "swedish")
        save_dir.chdir()
        assert Path.cwd() == save_dir

    def test_chef(self):
        p = Path(self.d, "swedish", "chef", "bork", "bork")
        assert p.read_file() == "bork!"

    def test_absolute(self):
        p1 = Path("images").absolute()
        p2 = self.d.child("images")
        assert p1 == p2

    def test_relative(self):
        p = self.d.child("images").relative()
        assert p == "images"

    def test_resolve(self):
        p1 = Path(self.link_to_images_dir, "image3.png")
        p2 = p1.resolve()
        assert p1.components()[-2:] == ["link_to_images_dir", "image3.png"]
        assert p2.components()[-2:] == ["images", "image3.png"]
        assert p1.exists()
        assert p2.exists()
        assert p1.same_file(p2)
        assert p2.same_file(p1)


class TestRelPathTo(FilesystemTest):
    def test1(self):
        p1 = Path("animals", "elephant")
        p2 = Path("animals", "mouse")
        assert p1.rel_path_to(p2) == Path("mouse")

    def test2(self):
        p1 = Path("animals", "elephant")
        p2 = Path("images", "image1.gif")
        assert p1.rel_path_to(p2) == Path(os.path.pardir, "images", "image1.gif")

    def test3(self):
        p1 = Path("animals", "elephant")
        assert p1.rel_path_to(self.d) == Path(os.path.pardir)

    def test4(self):
        p1 = Path("swedish", "chef")
        assert p1.rel_path_to(self.d) == Path(os.path.pardir, os.path.pardir)


class TestListingDirectories(FilesystemTest):
    def test_listdir_names_only(self):
        result = self.images.listdir(names_only=True)
        control = ["image1.gif", "image2.jpg", "image3.png"]
        assert result == control

    def test_listdir_arg_errors(self):
        with pytest.raises(TypeError):
            self.d.listdir(filter=FILES, names_only=True)

    def test_listdir(self):
        result = Path("images").listdir()
        control = [
            Path("images", "image1.gif"),
            Path("images", "image2.jpg"),
            Path("images", "image3.png")]
        assert result == control

    def test_listdir_all(self):
        result = Path("").listdir()
        control = [
            "a_file",
            "animals",
            "dead_link",
            "images",
            "link_to_chef_file",
            "link_to_images_dir",
            "swedish",
        ]
        assert result == control

    def test_listdir_files(self):
        result = Path("").listdir(filter=FILES)
        control = [
            "a_file",
            "link_to_chef_file",
        ]
        assert result == control

    def test_listdir_dirs(self):
        result = Path("").listdir(filter=DIRS)
        control = [
            "animals",
            "images",
            "link_to_images_dir",
            "swedish",
        ]
        assert result == control

    @pytest.mark.skipif("not hasattr(os, 'symlink')")
    def test_listdir_links(self):
        result = Path("").listdir(filter=LINKS)
        control = [
            "dead_link",
            "link_to_chef_file",
            "link_to_images_dir",
            ]
        assert result == control

    def test_listdir_files_no_links(self):
        result = Path("").listdir(filter=FILES_NO_LINKS)
        control = [
            "a_file",
        ]
        assert result == control

    def test_listdir_dirs_no_links(self):
        result = Path("").listdir(filter=DIRS_NO_LINKS)
        control = [
            "animals",
            "images",
            "swedish",
        ]
        assert result == control

    def test_listdir_dead_links(self):
        result = Path("").listdir(filter=DEAD_LINKS)
        control = [
            "dead_link",
        ]
        assert result == control

    def test_listdir_pattern_names_only(self):
        result = self.images.name.listdir("*.jpg", names_only=True)
        control = ["image2.jpg"]
        assert result == control

    def test_listdir_pattern(self):
        result = self.images.name.listdir("*.jpg")
        control = [Path("images", "image2.jpg")]
        assert result == control

    def test_walk(self):
        result = list(self.d.walk())
        control = [
            Path(self.a_file),
            Path(self.animals),
            Path(self.animals, "elephant"),
            Path(self.animals, "gonzo"),
            Path(self.animals, "mouse"),
        ]
        result = result[:len(control)]
        assert result == control

    def test_walk_bottom_up(self):
        result = list(self.d.walk(top_down=False))
        control = [
            Path(self.a_file),
            Path(self.animals, "elephant"),
            Path(self.animals, "gonzo"),
            Path(self.animals, "mouse"),
            Path(self.animals),
        ]
        result = result[:len(control)]
        assert result == control

    def test_walk_files(self):
        result = list(self.d.walk(filter=FILES))
        control = [
            Path(self.a_file),
            Path(self.animals, "elephant"),
            Path(self.animals, "gonzo"),
            Path(self.animals, "mouse"),
            Path(self.images, "image1.gif"),
        ]
        result = result[:len(control)]
        assert result == control

    def test_walk_dirs(self):
        result = list(self.d.walk(filter=DIRS))
        control = [
            Path(self.animals),
            Path(self.images),
            Path(self.link_to_images_dir),
            Path(self.d, "swedish"),
            ]
        result = result[:len(control)]
        assert result == control

    def test_walk_links(self):
        result = list(self.d.walk(filter=LINKS))
        control = [
            Path(self.dead_link),
            Path(self.link_to_chef_file),
            Path(self.link_to_images_dir),
            ]
        result = result[:len(control)]
        assert result == control


class TestStatAttributes(FilesystemTest):
    def test_exists(self):
        assert self.a_file.exists()
        assert self.images.exists()
        assert self.link_to_chef_file.exists()
        assert self.link_to_images_dir.exists()
        assert not self.dead_link.exists()
        assert not self.missing.exists()

    def test_lexists(self):
        assert self.a_file.lexists()
        assert self.images.lexists()
        assert self.link_to_chef_file.lexists()
        assert self.link_to_images_dir.lexists()
        assert self.dead_link.lexists()
        assert not self.missing.lexists()

    def test_isfile(self):
        assert self.a_file.isfile()
        assert not self.images.isfile()
        assert self.link_to_chef_file.isfile()
        assert not self.link_to_images_dir.isfile()
        assert not self.dead_link.isfile()
        assert not self.missing.isfile()

    def test_isdir(self):
        assert not self.a_file.isdir()
        assert self.images.isdir()
        assert not self.link_to_chef_file.isdir()
        assert self.link_to_images_dir.isdir()
        assert not self.dead_link.isdir()
        assert not self.missing.isdir()

    def test_islink(self):
        assert not self.a_file.islink()
        assert not self.images.islink()
        assert self.link_to_chef_file.islink()
        assert self.link_to_images_dir.islink()
        assert self.dead_link.islink()
        assert not self.missing.islink()

    def test_ismount(self):
        # Can't test on a real mount point because we don't know where it is
        assert not self.a_file.ismount()
        assert not self.images.ismount()
        assert not self.link_to_chef_file.ismount()
        assert not self.link_to_images_dir.ismount()
        assert not self.dead_link.ismount()
        assert not self.missing.ismount()

    def test_times(self):
        self.set_times()
        assert self.a_file.mtime() == 50000
        assert self.a_file.atime() == 60000
        # Can't set ctime to constant, so just make sure it returns a positive number.
        assert self.a_file.ctime() > 0

    def test_size(self):
        assert self.chef.size() == 5

    def test_same_file(self):
        if hasattr(self.a_file, "same_file"):
            control = Path(self.d, "a_file")
            assert self.a_file.same_file(control)
            assert not self.a_file.same_file(self.chef)

    def test_stat(self):
        st = self.chef.stat()
        assert hasattr(st, "st_mode")

    def test_statvfs(self):
        if hasattr(self.images, "statvfs"):
            stv = self.images.statvfs()
            assert hasattr(stv, "f_files")

    def test_chmod(self):
        self.a_file.chmod(0o600)
        newmode = self.a_file.stat().st_mode
        assert newmode & 0o777 == 0o600

    # Can't test chown: requires root privilege and knowledge of local users.

    def set_times(self):
        self.a_file.set_times()
        self.a_file.set_times(50000)
        self.a_file.set_times(50000, 60000)


class TestCreateRenameRemove(FilesystemTest):
    def test_mkdir_and_rmdir(self):
        self.missing.mkdir()
        assert self.missing.isdir()
        self.missing.rmdir()
        assert not self.missing.exists()

    def test_mkdir_and_rmdir_with_parents(self):
        abc = Path(self.d, "a", "b", "c")
        abc.mkdir(parents=True)
        assert abc.isdir()
        abc.rmdir(parents=True)
        assert not Path(self.d, "a").exists()

    def test_remove(self):
        self.a_file.remove()
        assert not self.a_file.exists()
        self.missing.remove()  # Removing a nonexistent file should succeed.

    if hasattr(os, 'symlink'):
        @pytest.mark.skipif("not hasattr(os, 'symlink')")
        def test_remove_broken_symlink(self):
            symlink = Path(self.d, "symlink")
            symlink.write_link("broken")
            assert symlink.lexists()
            symlink.remove()
            assert not symlink.lexists()

        @pytest.mark.skipif("not hasattr(os, 'symlink')")
        def test_rmtree_broken_symlink(self):
            symlink = Path(self.d, "symlink")
            symlink.write_link("broken")
            assert symlink.lexists()
            symlink.rmtree()
            assert not symlink.lexists()

    def test_rename(self):
        a_file = self.a_file
        b_file = Path(a_file.parent, "b_file")
        a_file.rename(b_file)
        assert not a_file.exists()
        assert b_file.exists()

    def test_rename_with_parents(self):
        pass  # @@MO: Write later.


class TestLinks(FilesystemTest):
    # @@MO: Write test_hardlink, test_symlink, test_write_link later.

    def test_read_link(self):
        assert self.dead_link.read_link() == "nowhere"

class TestHighLevel(FilesystemTest):
    def test_copy(self):
        a_file = self.a_file
        b_file = Path(a_file.parent, "b_file")
        a_file.copy(b_file)
        assert b_file.exists()
        a_file.copy_stat(b_file)

    def test_copy_tree(self):
        return  # .copy_tree() not implemented.
        images = self.images
        images2 = Path(self.images.parent, "images2")
        images.copy_tree(images2)

    def test_move(self):
        a_file = self.a_file
        b_file = Path(a_file.parent, "b_file")
        a_file.move(b_file)
        assert not a_file.exists()
        assert b_file.exists()

    def test_needs_update(self):
        control_files = self.images.listdir()
        self.a_file.set_times()
        assert not self.a_file.needs_update(control_files)
        time.sleep(1)
        control = Path(self.images, "image2.jpg")
        control.set_times()
        result = self.a_file.needs_update(self.images.listdir())
        assert self.a_file.needs_update(control_files)

    def test_read_file(self):
        assert self.chef.read_file() == "bork!"

    # .write_file and .rmtree tested in .setUp.



        
