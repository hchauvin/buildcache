# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Hadrien Chauvin

"""Checksum/digest various objects and resources."""

import os
import hashlib
import json


def digest_files(files):
    """
    Digests a list of files and directories.

    The directories are processed recursively.

    Args:
        files: A list of file paths.

    Return:
        A dictionary of file name to hex digests.
    """
    digests = {}
    for file in files:
        if os.path.islink(file):
            digests = {**digests, file: 'symlink=' + os.readlink(file)}
        elif os.path.isdir(file):
            digests = {
                **digests,
                **digest_files(
                    [os.path.join(file, name) for name in os.listdir(file)])
            }
        else:
            digests = {**digests, file: 'sha256=' + _digest_file(file)}
    return digests


def _digest_file(file):
    """
    Digests a single file.

    Args:
        file: The path to the file to digest.

    Return:
        A hex digest (a string).
    """
    BUF_SIZE = 65536

    m = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            buf = f.read(BUF_SIZE)
            if not buf:
                break
            m.update(buf)

    return m.hexdigest()


def digest_string(s):
    """
    Digests a string.

    Args:
        s: The string to digest.

    Return:
        A hex digest (a string).
    """
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    return m.hexdigest()


def digest_json(o):
    return digest_string(json.dumps(o, sort_keys=True))