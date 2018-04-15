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

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_bool


GCS_CONFIGS = UnspecifiedConfigSection(
  'gcs_config',
  help='Configuration for GCS FS',
  each=ConfigSection(
    help='Information about the GCS Configuration',
    members=dict(
      ALLOW_ENVIRONMENT_CREDENTIALS=Config(
        help='Allow to use environment sources of credentials (metadata service).',
        key='allow_environment_credentials',
        default=True,
        type=coerce_bool
      ),
      BUCKETS=Config(
        help='Which buckets are visible to this instance (csv)',
        key='buckets',
        required=True,
        type=str
      )
    )
  )
)


def config_validator(user):
  res = []

  if GCS_CONFIGS.keys():
    if 'default' not in GCS_CONFIG.keys():
      res.append(('gcs.config', 'No Default GCS configuration found'))

    for name in GCS_CONFIGS.keys():
      buckets = GCS_CONFIGS[name].BUCKETS.get()
      if region_name not in region_names:
        res.append(('aws.aws_accounts.%s.region' % name, 'Unknown region %s' % region_name))

  return res