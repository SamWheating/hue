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

from google.cloud import storage


class Client(object):
  def __init__(self, buckets=None):
    self._buckets = buckets


  @classmethod
  def from_config(cls, conf):
    buckets = conf.GCS_CONFIGURED_BUCKETS.get()
    env_cred_allowed = conf.ALLOW_ENVIRONMENT_CREDENTIALS.get()

    #if None in (access_key_id, secret_access_key) and not env_cred_allowed:
    #  raise ValueError('Can\'t create AWS client, credential is not configured')

    return cls(
      buckets=buckets.split(',')
    )

  def get_gcs_connection(self):
    # TODO: add auth from json service account file or oauth flow
    # ideally use the user tocken we got from oauth
    connection = storage.client()
    if connection is None:
      raise ValueError('Cannot create GCS Client Connection')
    return connection