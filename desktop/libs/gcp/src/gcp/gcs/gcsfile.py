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

import io, errno

from gcp.gcs import translate_gcs_error

DEFAULT_READ_SIZE = 1024 * 1024  # 1MB


def open(key, mode='r'):
  if mode == 'r':
    return _ReadableGCSFile(key)
  else:
    raise IOError(errno.EINVAL, 'Unavailable mode "%s"' % mode)


class _ReadableGCSFile():
  def __init__(self, blob):
      self._fh_bytes = bytearray()
      self._fh = io.BytesIO(self._fh_bytes)
      # For now we're just going to download the whole file.
      # TODO: implement a File like object that will keep track of seek pos
      # and read chunks of the file
      # https://chromium.googlesource.com/external/boto/+/HEAD/boto/s3/keyfile.py
      blob.download_to_file(self._fh)
      self._fh.seek(0)
  
  @translate_gcs_error
  def read(self, length=DEFAULT_READ_SIZE):
    return self._fh.read(length)