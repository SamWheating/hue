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

from nose.tools import eq_

from gcp.gcs.gcsstat import GCSStat


def test_derivable_properties():
  s = GCSStat('foo', 'gs://bar/foo', False, 40, 1424983327)
  eq_('FILE', s.type)
  eq_(0666 | stat.S_IFREG, s.mode)
  eq_('', s.user)
  eq_('', s.group)
  eq_(1424983327, s.atime)
  eq_(False, s.aclBit)

  s = GCSStat('bar', 'gs://bar', True, 0, 1424983327)
  eq_('DIRECTORY', s.type)
  eq_(0777 | stat.S_IFDIR, s.mode)


def test_from_bucket():
  s = GCSStat.from_bucket(FakeBucket('boo'))
  eq_('DIRECTORY', s.type)
  eq_('boo', s.name)
  eq_('gs://boo', s.path)
  eq_(0, s.size)
  eq_(0, s.atime)


def test_from_key():
  blob = FakeBlob('foo', FakeBucket('bar'), 42, 'Thu, 26 Feb 2015 20:42:07 GMT')
  s = GCSStat.from_blob(blob)
  eq_('FILE', s.type)
  eq_('foo', s.name)
  eq_('gs://bar/foo', s.path)
  eq_(42, s.size)
  eq_(1424983327, s.mtime)

  blob.size = None
  blob.updated = None
  s = GCSStat.from_blob(blob, is_dir=True)
  eq_('DIRECTORY', s.type)
  eq_(0, s.size)
  eq_(0, s.atime)


def test_for_gcs_root():
  s = GCSStat.for_gcs_root()
  eq_('DIRECTORY', s.type)
  eq_('GCS', s.name)
  eq_('gs://', s.path)
  eq_(0, s.size)
  eq_(0, s.atime)


class FakeBucket(object):
  def __init__(self, name):
    self.name = name


class FakeBlob(object):
  def __init__(self, name, bucket, size=None, updated=None):
    self.name = name
    self.bucket = bucket
    self.size = size
    self.updated = updated
