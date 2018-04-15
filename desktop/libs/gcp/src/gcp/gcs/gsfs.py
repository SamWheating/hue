# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import sys

import errno
import itertools
import logging
import os
import posixpath

#from boto.exception import S3ResponseError
#from boto.s3  blob import Key
#from boto.s3.prefix import Prefix

from gcp import gcs
from gcp.gcs import translate_gcs_error, gcsfile
from gcp.gcs.gcsstat import GCSStat

from hadoop.fs import normpath


DEFAULT_READ_SIZE = 1024 * 1024  # 1MB
LOG = logging.getLogger(__name__)


class GCSFileSystem(object):
  def __init__(self, gcs_connection):
    self._gcs_connection = gcs_connection
    self._bucket_cache = None

  def _init_bucket_cache(self):
    if self._bucket_cache is None:
      buckets = self._gcs_connection.get_all_buckets()
      self._bucket_cache = {}
      for bucket in buckets:
        self._bucket_cache[bucket.name] = bucket

  def _get_bucket(self, name):
    self._init_bucket_cache()
    if name not in self._bucket_cache:
      self._bucket_cache[name] = self._gcs_connection.get_bucket(name)
    return self._bucket_cache[name]

  def _get_blob(self, path, validate=True):
    bucket_name, key_name = gcs.parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)
    try:
      blob = bucket.get_blob(key_name)
      if not validate and blob is None:
          blob = bucket.blob(key_name)
      return blob
    except:
      e, exc, tb = sys.exc_info()
      raise ValueError(e)

  def _stats(self, path):
    if gcs.is_root(path):
      return GCSStat.for_gcs_root()

    blob = self._get_blob(path)

    if  blob is None:
      blob = self._get_blob (path, validate=False)
    return self._stats_blob(blob)

  @staticmethod
  def _stats_blob(blob):
    if blob.size is not None:
      is_directory_name = not blob.name or blob.name[-1] == '/'
      return GCSStat.from_blob(blob, is_dir=is_directory_name)
    else:
      blob.name = GCSFileSystem._append_separator(blob.name)
      ls =  blob.bucket.list_blobs(prefix=blob.name, max_results=1)
      if len(ls) > 0:
        return GCSStat.from_blob(blob, is_dir=True)
    return None

  @staticmethod
  def _append_separator(path):
    if path and not path.endswith('/'):
      path += '/'
    return path

  @staticmethod
  def _cut_separator(path):
    return path.endswith('/') and path[:-1] or path

  @staticmethod
  def isroot(path):
    return gcs.is_root(path)

  @staticmethod
  def join(*comp_list):
    return gcs.join(*comp_list)

  @staticmethod
  def normpath(path):
    return normpath(path)

  @translate_gcs_error
  def open(self, path, mode='r'):
    blob = self._get_blob(path, validate=True)
    if blob is None:
      raise IOError(errno.ENOENT, "No such file or directory: '%s'" % path)
    return gcsfile.open(blob, mode=mode)

  @translate_gcs_error
  def read(self, path, offset, length):
    fh = self.open(path, 'r')
    fh.seek(offset, os.SEEK_SET)
    return fh.read(length)

  @translate_gcs_error
  def isfile(self, path):
    stat = self._stats(path)
    if stat is None:
      return False
    return not stat.isDir

  @translate_gcs_error
  def isdir(self, path):
    stat = self._stats(path)
    if stat is None:
      return False
    return stat.isDir

  @translate_gcs_error
  def exists(self, path):
    return self._stats(path) is not None

  @translate_gcs_error
  def stats(self, path):
    path = normpath(path)
    stats = self._stats(path)
    if stats:
      return stats
    raise IOError(errno.ENOENT, "No such file or directory: '%s'" % path)

  @translate_gcs_error
  def listdir_stats(self, path, glob=None):
    if glob is not None:
      raise NotImplementedError("Option `glob` is not implemented")

    if gcs.is_root(path):
      self._init_bucket_cache()
      return [GCSStat.from_bucket(b) for b in self._bucket_cache.values()]

    bucket_name, prefix = gcs.parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)
    prefix = self._append_separator(prefix)
    res = []
    for item in bucket.list(prefix=prefix, delimiter='/'):
      if isinstance(item, Prefix):
        res.append(GCSStat.from_key(Key(item.bucket, item.name), is_dir=True))
      else:
        if item.name == prefix:
          continue
        res.append(self._stats_blob(item))
    return res

  def listdir(self, path, glob=None):
    return [gcs.parse_uri(x.path)[2] for x in self.listdir_stats(path, glob)]

  @translate_gcs_error
  def rmtree(self, path, skipTrash=False):
    if not skipTrash:
      raise NotImplementedError('Moving to trash is not implemented for GCS')
    blob = self._get_blob(path, validate=False)

    if blob.exists():
      to_delete = iter([blob])
    else:
      to_delete = iter([])

    if self.isdir(path):
      # add `/` to prevent removing of `s3://b/a_new` trying to remove `s3://b/a`
      prefix = self._append_separator(blob.name)
      blobs =  blob.bucket.list_blobs(prefix=prefix)
      to_delete = itertools.chain(blobs, to_delete)
    result =  blob.bucket.delete_blobs(to_delete)
    if result.errors:
      msg = "%d errors occurred during deleting '%s':\n%s" % (
        len(result.errors),
        '\n'.join(map(repr, result.errors)))
      LOG.error(msg)
      raise IOError(msg)

  @translate_gcs_error
  def remove(self, path, skip_trash=False):
    if not skip_trash:
      raise NotImplementedError('Moving to trash is not implemented for GCS')
    blob = self._get_blob(path, validate=False)
    blob.bucket.delete_blob (blob.name)

  def restore(self, *args, **kwargs):
    raise NotImplementedError('Moving to trash is not implemented for GCS')

  @translate_gcs_error
  def mkdir(self, path, *args, **kwargs):
    """
    Creates a directory and any parent directory if necessary.

    Actually it creates an empty object: gs://[bucket]/[path]/
    """
    stats = self._stats(path)
    if stats:
      if stats.isDir:
        return None
      else:
        raise IOError(errno.ENOTDIR, "'%s' already exists and is not a directory" % path)
    path = self._append_separator(path)  # folder  blob should ends by /
    self.create(path)  # create empty object

  @translate_gcs_error
  def copy(self, src, dst, recursive=False, *args, **kwargs):
    self._copy(src, dst, recursive=recursive, use_src_basename=True)

  @translate_gcs_error
  def copyfile(self, src, dst, *args, **kwargs):
    if self.isdir(dst):
      raise IOError(errno.EINVAL, "Copy dst '%s' is a directory" % dst)
    self._copy(src, dst, recursive=False, use_src_basename=False)

  @translate_gcs_error
  def copy_remote_dir(self, src, dst, *args, **kwargs):
    self._copy(src, dst, recursive=True, use_src_basename=False)

  def _copy(self, src, dst, recursive, use_src_basename):
    src_st = self.stats(src)
    if src_st.isDir and not recursive:
      return # omitting directory

    dst = gcs.abspath(src, dst)
    dst_st = self._stats(dst)
    if src_st.isDir and dst_st and not dst_st.isDir:
      raise IOError(errno.EEXIST, "Cannot overwrite non-directory '%s' with directory '%s'" % (dst, src))

    src_bucket, src_key = gcs.parse_uri(src)[:2]
    dst_bucket, dst_key = gcs.parse_uri(dst)[:2]

    keep_src_basename = use_src_basename and dst_st and dst_st.isDir
    src_bucket = self._get_bucket(src_bucket)
    dst_bucket = self._get_bucket(dst_bucket)

    if keep_src_basename:
      cut = len(posixpath.dirname(src_key))  # cut of an parent directory name
      if cut:
        cut += 1
    else:
      cut = len(src_key)
      if not src_key.endswith('/'):
        cut += 1

    for blob in src_bucket.list(prefix=src_key):
      if not blob.name.startswith(src_key):
        raise RuntimeError("Invalid  blob to transform: %s" %  blob.name)
      dst_name = posixpath.normpath(gcs.join(dst_key, blob.name[cut:]))
      src_bucket.copy(blob, dst_bucket, dst_name)

  @translate_gcs_error
  def rename(self, old, new):
    old.bucket.rename_blob(old, new)

  @translate_gcs_error
  def rename_star(self, old_dir, new_dir):
    if not self.isdir(old_dir):
      raise IOError(errno.ENOTDIR, "'%s' is not a directory" % old_dir)
    if self.isfile(new_dir):
      raise IOError(errno.ENOTDIR, "'%s' is not a directory" % new_dir)
    ls = self.listdir(old_dir)
    for entry in ls:
      self.rename(gcs.join(old_dir, entry), gcs.join(new_dir, entry))

  @translate_gcs_error
  def create(self, path, overwrite=False, data=None):
    blob = self._get_blob(path, validate=False)
    if overwrite or self._get_blob(path) is None:
      blob.upload_from_string(data or '')

  @translate_gcs_error
  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    local_src = self._cut_separator(local_src)
    remote_dst = self._cut_separator(remote_dst)

    def _copy_file(src, dst):
      blob = self._get_blob(dst, validate=False)
      fp = open(src, 'r')
      blob.upload_from_file(fp)

    if os.path.isdir(local_src):
      for (local_dir, sub_dirs, files) in os.walk(local_src, followlinks=False):
        remote_dir = local_dir.replace(local_src, remote_dst)

        if not sub_dirs and not files:
          self.mkdir(remote_dir)
        else:
          for file_name in files:
            _copy_file(os.path.join(local_dir, file_name), os.path.join(remote_dir, file_name))
    else:
      file_name = os.path.split(local_src)[1]
      if self.isdir(remote_dst):
        remote_file = os.path.join(remote_dst, file_name)
      else:
        remote_file = remote_dst
      _copy_file(local_src, remote_file)

  def setuser(self, user):
    pass  # user-concept doesn't have sense for this implementation
