# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Hadrien Chauvin

import os
import shutil
import buildcache.checksum


class Cache:
    """A CircleCI-inspired cache.

    The cache is a local folder.  It contains subfolders, one per cache key.
    It is used to cache I/O operations made on a working directory.

    When you restore a cache entry given its key, its content is merged
    with the working directory.

    When you save a cache entry given its key, you replace its
    content with the subset of the working directory that you select.
    """

    def __init__(self, workdir, cachedir):
        self._workdir = workdir
        self._cachedir = cachedir

    def restore(self, keys):
        """Restores the first cache entry whose key exists.

        Args:
            keys: A list of keys to try.
        """
        for key in keys:
            if os.path.exists(os.path.join(self._cachedir, key)):
                print(f"Cache {key} found")
                self._restore_for_key(key)
                return
        print(f"No cache found")

    def save(self, key, paths):
        """Saves a subset of the working directory to a cache entry.

        If the cache entry exists, its content is entirely overwritten.

        Args:
            key: The key of the cache entry to save.
            paths: Paths, relative to the working directory, to save into
                the cache entry.  Symlinks are included as is, and folders
                are recursively copied.
        """
        shutil.rmtree(os.path.join(self._cachedir, key), ignore_errors=True)
        for path in paths:
            os.makedirs(os.path.join(self._cachedir, key, os.path.dirname(path)))
            abs_path = os.path.join(self._workdir, path)
            if os.path.isdir(abs_path):
                shutil.copytree(abs_path, os.path.join(self._cachedir, key, path))
            else:
                shutil.copy2(abs_path, os.path.join(self._cachedir, key, path))

    def _restore_for_key(self, key):
        """
        Restores the cache for a given tree.

        Args:
            key: The cache key.
        """
        path = os.path.join(self._cachedir, key)
        for root, dirs, files in os.walk(path):
            for d in dirs:
                dest = os.path.join(os.path.relpath(root, path), d)
                if not os.path.exists(dest):
                    os.mkdir(dest)
            for f in files:
                shutil.copy2(
                    os.path.join(root, f),
                    os.path.join(os.path.relpath(root, path), f))

    def checksum(self, paths):
        """
        Checksums all the files in a list of paths walked through recursively.
        The traversal is deterministic.

        The digest can be used to cache the result of some operations depending
        on the content of its inputs.

        Args:
            paths: The paths to traverse, relative to the working directory.

        Return:
            A hex digest (a string) of the content of these paths.
        """
        return checksum.digest_json(checksum.digest_files([
            os.path.join(self._workdir, path) for path in paths
        ]))