#!/usr/bin/env python
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

import logging
import re

# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#
# For now though we have to load in the monkey patches here because we know
# this file has been loaded after `desktop.settings` has been loaded.
import desktop.monkey_patches

import desktop.lib.metrics.file_reporter
desktop.lib.metrics.file_reporter.start_file_reporter()

from django.conf import settings
from django.conf.urls import include
from django.contrib import admin

from desktop import appmanager
from desktop.conf import METRICS, USE_NEW_EDITOR
from django.conf.urls import url


# Django expects handler404 and handler500 to be defined.
# django.conf.urls provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler403 = 'desktop.views.serve_403_error'
handler404 = 'desktop.views.serve_404_error'
handler500 = 'desktop.views.serve_500_error'


admin.autodiscover()

# Some django-wide URLs
dynamic_patterns = [
  url(r'^accounts/login/$', include('desktop.auth.views.dt_login')),
  url(r'^accounts/logout/$', include('desktop.auth.views.dt_logout'), {'next_page': '/'}),
  url(r'^profile$', include('desktop.auth.views.profile')),
  url(r'^login/oauth/?$', include('desktop.auth.views.oauth_login')),
  url(r'^login/oauth_authenticated/?$', include('desktop.auth.views.oauth_authenticated')),
]



if USE_NEW_EDITOR.get():
  dynamic_patterns += [
    url(r'^home$',include('desktop.views.home2')),
    url(r'^home2$',include('desktop.views.home')),
    url(r'^home_embeddable$',include('desktop.views.home_embeddable')),
  ]

else:
  dynamic_patterns += [
    url(r'^home$',include('desktop.views.home')),
    url(r'^home2$',include('desktop.views.home2'))
  ]

dynamic_patterns += [
  url(r'^logs$',include('desktop.views.log_view')),
  url(r'^desktop/dump_config$',include('desktop.views.dump_config')),
  url(r'^desktop/download_logs$',include('desktop.views.download_log_view')),
  url(r'^desktop/get_debug_level',include('desktop.views.get_debug_level')),
  url(r'^desktop/set_all_debug',include('desktop.views.set_all_debug')),
  url(r'^desktop/reset_all_debug',include('desktop.views.reset_all_debug')),
  url(r'^bootstrap.js$', include('desktop.views.bootstrap')), # unused
  url(r'^desktop/prefs/(?P<key>\w+)?$', include('desktop.views.prefs')),
  url(r'^desktop/status_bar/?$', include('desktop.views.status_bar')),
  url(r'^desktop/debug/is_alive$',include('desktop.views.is_alive')),
  url(r'^desktop/debug/is_idle$',include('desktop.views.is_idle')),
  url(r'^desktop/debug/threads$', include('desktop.views.threads')),
  url(r'^desktop/debug/memory$', include('desktop.views.memory')),
  url(r'^desktop/debug/check_config$', include('desktop.views.check_config')),
  url(r'^desktop/debug/check_config_ajax$', include('desktop.views.check_config_ajax')),
  url(r'^desktop/log_frontend_event$', include('desktop.views.log_frontend_event')),
  

  # Mobile
  url(r'^assist_m', include('desktop.views.assist_m')),
  # Responsive
  url(r'^responsive', include('desktop.views.responsive')),

  # KO components, change to doc?name=ko_editor or similar
  url(r'^ko_editor', include('desktop.views.ko_editor')),
  url(r'^ko_metastore', include('desktop.views.ko_metastore')),

  # Jasmine
  url(r'^jasmine', include('desktop.views.jasmine')),

  # Unsupported browsers
  url(r'^boohoo$',include('desktop.views.unsupported')),

  # Top level web page!
  url(r'^$', include('desktop.views.index')),
]

dynamic_patterns += [
  # Tags
  url(r'^desktop/api/tag/add_tag$', include('desktop.api.add_tag')),
  url(r'^desktop/api/tag/remove_tag$', include('desktop.api.remove_tag')),
  url(r'^desktop/api/doc/tag$', include('desktop.api.tag')),
  url(r'^desktop/api/doc/update_tags$', include('desktop.api.update_tags')),
  url(r'^desktop/api/doc/get$', include('desktop.api.get_document')),

  # Permissions
  url(r'^desktop/api/doc/update_permissions', include('update_permissions')),
]

dynamic_patterns += [
  url(r'^desktop/api2/doc/open?$', include('desktop.api2.open_document')),  # To keep before get_document
  url(r'^desktop/api2/docs/?$', include('desktop.api2.search_documents')),  # search documents for current user
  url(r'^desktop/api2/doc/?$', include('desktop.api2.get_document')),  # get doc/dir by path or UUID

  url(r'^desktop/api2/doc/move/?$', include('desktop.api2.move_document')),
  url(r'^desktop/api2/doc/mkdir/?$', include('desktop.api2.create_directory')),
  url(r'^desktop/api2/doc/update/?$', include('desktop.api2.update_document')),
  url(r'^desktop/api2/doc/delete/?$', include('desktop.api2.delete_document')),
  url(r'^desktop/api2/doc/restore/?$', include('desktop.api2.restore_document')),
  url(r'^desktop/api2/doc/share/?$', include('desktop.api2.share_document')),

  url(r'^desktop/api2/doc/export/?$', include('desktop.api2.export_documents')),
  url(r'^desktop/api2/doc/import/?$', include('desktop.api2.import_documents')),

  url(r'^desktop/api/search/entities/?$', include('desktop.api2.search_entities')),
  url(r'^desktop/api/search/entities_interactive/?$', include('desktop.api2.search_entities_interactive')),
]

# Default Configurations
dynamic_patterns += [
  url(r'^desktop/api/configurations/?$', include('desktop.configuration.api.default_configurations')),
  url(r'^desktop/api/configurations/user/?$', include('desktop.configuration.api.app_configuration_for_user')),
  url(r'^desktop/api/configurations/delete/?$', include('desktop.configuration.api.delete_default_configuration')),
]

dynamic_patterns += [url(r'^desktop/api/users/autocomplete', include('useradmin.views.list_for_autocomplete'))]

# Metrics specific
if METRICS.ENABLE_WEB_METRICS.get():
  dynamic_patterns += [url(r'^desktop/metrics/', include('desktop.lib.metrics.urls'))]

dynamic_patterns += [url(r'^admin/', include(admin.site.urls))]

static_patterns = []

# SAML specific
if settings.SAML_AUTHENTICATION:
  static_patterns.append(url(r'^saml2/', include('libsaml.urls')))

# OpenId specific
if settings.OPENID_AUTHENTICATION:
    static_patterns.append(url(r'^openid/', include('libopenid.urls')))

if settings.OAUTH_AUTHENTICATION:
  static_patterns.append(url(r'^oauth/', include('liboauth.urls')))

# Root each app at /appname if they have a "urls" module
for app in appmanager.DESKTOP_MODULES:
  if app.urls:
    if app.is_url_namespaced:
      namespace = {'namespace': app.name, 'app_name': app.name}
    else:
      namespace = {}
    if namespace or app in appmanager.DESKTOP_APPS:
      dynamic_patterns.extend(url('^' + re.escape(app.name) + '/', include(app.urls, **namespace)))
      app.urls_imported = True

static_patterns.append(
    (r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
      'django.views.static.serve',
      { 'document_root': settings.STATIC_ROOT })
)

urlpatterns = static_patterns + dynamic_patterns

for x in dynamic_patterns:
  logging.debug("Dynamic pattern: %s" % (x,))
for x in static_patterns:
  logging.debug("Static pattern: %s" % (x,))
