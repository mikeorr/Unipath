import os
import stat

import pytest

from unipath import Path


@pytest.mark.parametrize("times", [False, True])
@pytest.mark.parametrize("perms", [False, True])
def test_copy_stat_respects_metadata_flags(tmp_path, times, perms):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.write_bytes(b"source")
    destination.write_bytes(b"destination")
    os.chmod(str(source), 0o600)
    os.chmod(str(destination), 0o644)
    os.utime(str(source), (1000000000, 1000000100))
    os.utime(str(destination), (1100000000, 1100000100))
    source_stat = source.stat()
    destination_stat = destination.stat()

    Path(str(source)).copy_stat(str(destination), times=times, perms=perms)

    actual = destination.stat()
    expected_times = source_stat if times else destination_stat
    expected_mode = source_stat if perms else destination_stat
    assert (actual.st_atime, actual.st_mtime) == (
        expected_times.st_atime, expected_times.st_mtime)
    assert stat.S_IMODE(actual.st_mode) == stat.S_IMODE(expected_mode.st_mode)
    assert destination.read_bytes() == b"destination"


@pytest.mark.parametrize("times", [False, True])
@pytest.mark.parametrize("perms", [False, True])
def test_copy_respects_metadata_flags(tmp_path, times, perms):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.write_bytes(b"source")
    destination.write_bytes(b"destination")
    os.chmod(str(source), 0o600)
    os.chmod(str(destination), 0o644)
    os.utime(str(source), (1000000000, 1000000100))
    os.utime(str(destination), (1100000000, 1100000100))
    destination_stat = destination.stat()

    Path(str(source)).copy(str(destination), times=times, perms=perms)

    actual = destination.stat()
    source_stat = source.stat()
    if times:
        assert (actual.st_atime, actual.st_mtime) == (
            source_stat.st_atime, source_stat.st_mtime)
    else:
        assert actual.st_atime == destination_stat.st_atime
        assert actual.st_mtime != source_stat.st_mtime
    expected_mode = source_stat if perms else destination_stat
    assert stat.S_IMODE(actual.st_mode) == stat.S_IMODE(expected_mode.st_mode)
    assert destination.read_bytes() == b"source"
