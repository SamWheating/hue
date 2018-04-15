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

import calendar
import errno
import logging
import posixpath
import re
import sys
import time

from functools import wraps

from google.cloud.exceptions import ClientError
from hadoop.fs import normpath


ERRNO_MAP = {
  403: errno.EACCES,
  404: errno.ENOENT
}
DEFAULT_ERRNO = errno.EINVAL

GCS_PATH_RE = re.compile('^/*[gG][sS]://([^/]+)(/(.*?([^/]+)?/?))?$')
GCS_ROOT = 'gs://'


def lookup_gcserror(error):
  err_no = ERRNO_MAP.get(error.status, DEFAULT_ERRNO)
  return IOError(err_no, error.reason)


def translate_gcs_error(fn):
  @wraps(fn)
  def wrapped(*args, **kwargs):
    try:
      return fn(*args, **kwargs)
    except ClientError:
      _, exc, tb = sys.exc_info()
      logging.error('GCS error: %s' % exc)
      lookup = lookup_gcserror(exc)
      raise lookup.__class__, lookup, tb
  return wrapped


def parse_uri(uri):
  """
  Returns tuple (bucket_name, key_name, key_basename).
  Raises ValueError if invalid GCS URI is passed.
  """
  match = GCS_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid GCS URI: %s" % uri)
  key = match.group(3) or ''
  basename = match.group(4) or ''
  return match.group(1), key, basename


def is_root(uri):
  """
  Check if URI is GCS root (GS://)
  """
  return uri.lower() == GCS_ROOT


def abspath(cd, uri):
  """
  Returns absolute URI, examples:

  abspath('gs://bucket/key', key2') == 'gs://bucket/key/key2'
  abspath('gs://bucket/key', 'gs://bucket2/key2') == 'gs://bucket2/key2'
  """
  if not uri.lower().startswith(GCS_ROOT):
    uri = normpath(join(cd, '..', uri))
  return uri


def join(*comp_list):
  def _prep(uri):
    try:
      return '/%s/%s' % parse_uri(uri)[:2]
    except ValueError:
      return '/' if is_root(uri) else uri
  joined = posixpath.join(*map(_prep, comp_list))
  if joined and joined[0] == '/':
    joined = 'gs:/%s' % joined
  return joined

