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

import stat
import posixpath

class GCSStat(object):
  DIR_MODE = 0777 | stat.S_IFDIR
  FILE_MODE = 0666 | stat.S_IFREG

  def __init__(self, name, path, isDir, size, mtime):
    self.name = name
    self.path = path
    self.isDir = isDir
    self.size = size
    self.mtime = mtime

  def __getitem__(self, blob):
#    try:
   return getattr(self, blob)
#    except AttributeError:
#      raise blobError(blob)

  def __setitem__(self, blob, value):
    # What about derivable values?
    setattr(self, blob, value)

  @property
  def type(self):
    return 'DIRECTORY' if self.isDir else 'FILE'

  @property
  def mode(self):
    return GCSStat.DIR_MODE if self.isDir else GCSStat.FILE_MODE

  @property
  def user(self):
    return ''

  @property
  def group(self):
    return ''

  @property
  def atime(self):
    return self.mtime

  @property
  def aclBit(self):
    return False

  @classmethod
  def from_bucket(cls, bucket):
    return cls(bucket.name, 'gs://%s' % bucket.name, True, 0, 0)

  @classmethod
  def from_blob(cls, blob, is_dir=False):
    if blob.name:
      name = posixpath.basename(blob.name[:-1] if blob.name[-1] == '/' else blob.name)
      path = 'gs://%s/%s' % (blob.bucket.name, blob.name)
    else:
      name = ''
      path = 'gs://%s' % blob.bucket.name

    size = blob.size or 0
    mtime = blob.updated.strftime('%s') if blob.updated else 0
    return cls(name, path, is_dir, size, mtime)

  @classmethod
  def for_gcs_root(cls):
    return cls('GCS', 'gs://', True, 0, 0)

  def to_json_dict(self):
    """
    Returns a dictionary for easy serialization
    """
    blobs = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group', 'aclBit')
    res = {}
    for k in blobs:
      res[k] = self[k]
    return res






