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

from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, eq_

from gcp import gcs


def test_parse_uri():
  p = gcs.parse_uri

  eq_(('bucket', 'folder/key', 'key'), p('gs://bucket/folder/key'))
  eq_(('bucket', 'folder/key/', 'key'), p('gs://bucket/folder/key/'))
  eq_(('bucket', 'folder/key/', 'key'), p('GS://bucket/folder/key/'))
  eq_(('bucket', '', ''), p('gs://bucket'))
  eq_(('bucket', '', ''), p('gs://bucket/'))

  assert_raises(ValueError, p, '/local/path')
  assert_raises(ValueError, p, 'ftp://ancient/archive')
  assert_raises(ValueError, p, 'gs:/missed/slash')
  assert_raises(ValueError, p, 'gs://')


def test_join():
  j = gcs.join
  eq_("gs://b", j("gs://", "b"))
  eq_("gs://b/f", j("gs://b", "f"))
  eq_("gs://b/f1/f2", j("gs://b", "f1", "f2"))
  eq_("gs://b/f1/f2/../f3", j("gs://b/f1/f2", "../f3"))


def test_abspath():
  raise SkipTest()

  a = gcs.abspath
  eq_('gs://a/b/d', a('gs://a/b/c', 'd'))
  eq_('gs://d', a('gs://a/b/c', 'gs://d'))


def test_is_root():
  i = gcs.is_root
  eq_(True, i('gs://'))
  eq_(True, i('GS://'))
  eq_(False, i('gs:/'))
  eq_(False, i('gs://bucket'))
  eq_(False, i('/local/path'))


