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
  url(r'^accounts/login/$', 'desktop.auth.views.dt_login'),
  url(r'^accounts/logout/$', 'desktop.auth.views.dt_logout', {'next_page': '/'}),
  url(r'^profile$', 'desktop.auth.views.profile'),
  url(r'^login/oauth/?$', 'desktop.auth.views.oauth_login'),
  url(r'^login/oauth_authenticated/?$', 'desktop.auth.views.oauth_authenticated'),
]



if USE_NEW_EDITOR.get():
  dynamic_patterns += [
    url(r'^home$','desktop.views.home2'),
    url(r'^home2$','desktop.views.home'),
    url(r'^home_embeddable$','desktop.views.home_embeddable'),
  ]

else:
  dynamic_patterns += [
    url(r'^home$','desktop.views.home'),
    url(r'^home2$','desktop.views.home2')
  ]

dynamic_patterns += [
  url(r'^logs$','desktop.views.log_view'),
  url(r'^desktop/dump_config$','desktop.views.dump_config'),
  url(r'^desktop/download_logs$','desktop.views.download_log_view'),
  url(r'^desktop/get_debug_level','desktop.views.get_debug_level'),
  url(r'^desktop/set_all_debug','desktop.views.set_all_debug'),
  url(r'^desktop/reset_all_debug','desktop.views.reset_all_debug'),
  url(r'^bootstrap.js$', 'desktop.views.bootstrap'), # unused
  url(r'^desktop/prefs/(?P<key>\w+)?$', 'desktop.views.prefs'),
  url(r'^desktop/status_bar/?$', 'desktop.views.status_bar'),
  url(r'^desktop/debug/is_alive$','desktop.views.is_alive'),
  url(r'^desktop/debug/is_idle$','desktop.views.is_idle'),
  url(r'^desktop/debug/threads$', 'desktop.views.threads'),
  url(r'^desktop/debug/memory$', 'desktop.views.memory'),
  url(r'^desktop/debug/check_config$', 'desktop.views.check_config'),
  url(r'^desktop/debug/check_config_ajax$', 'desktop.views.check_config_ajax'),
  url(r'^desktop/log_frontend_event$', 'desktop.views.log_frontend_event'),
  ]

  # Mobile
  url(r'^assist_m', 'desktop.views.assist_m'),
  # Responsive
  url(r'^responsive', 'desktop.views.responsive'),

  # KO components, change to doc?name=ko_editor or similar
  url(r'^ko_editor', 'desktop.views.ko_editor'),
  url(r'^ko_metastore', 'desktop.views.ko_metastore'),

  # Jasmine
  url(r'^jasmine', 'desktop.views.jasmine'),

  # Unsupported browsers
  url(r'^boohoo$','desktop.views.unsupported'),

  # Top level web page!
  url(r'^$', 'desktop.views.index'),
)

dynamic_patterns += [
  # Tags
  url(r'^desktop/api/tag/add_tag$', 'desktop.api.add_tag'),
  url(r'^desktop/api/tag/remove_tag$', 'desktop.api.remove_tag'),
  url(r'^desktop/api/doc/tag$', 'desktop.api.tag'),
  url(r'^desktop/api/doc/update_tags$', 'desktop.api.update_tags'),
  url(r'^desktop/api/doc/get$', 'desktop.api.get_document'),

  # Permissions
  url(r'^desktop/api/doc/update_permissions', 'update_permissions'),
]

dynamic_patterns += [
  url(r'^desktop/api2/doc/open?$', 'desktop.api2.open_document'),  # To keep before get_document
  url(r'^desktop/api2/docs/?$', 'desktop.api2.search_documents'),  # search documents for current user
  url(r'^desktop/api2/doc/?$', 'desktop.api2.get_document'),  # get doc/dir by path or UUID

  url(r'^desktop/api2/doc/move/?$', 'desktop.api2.move_document'),
  url(r'^desktop/api2/doc/mkdir/?$', 'desktop.api2.create_directory'),
  url(r'^desktop/api2/doc/update/?$', 'desktop.api2.update_document'),
  url(r'^desktop/api2/doc/delete/?$', 'desktop.api2.delete_document'),
  url(r'^desktop/api2/doc/restore/?$', 'desktop.api2.restore_document'),
  url(r'^desktop/api2/doc/share/?$', 'desktop.api2.share_document'),

  url(r'^desktop/api2/doc/export/?$', 'desktop.api2.export_documents'),
  url(r'^desktop/api2/doc/import/?$', 'desktop.api2.import_documents'),

  url(r'^desktop/api/search/entities/?$', 'desktop.api2.search_entities'),
  url(r'^desktop/api/search/entities_interactive/?$', 'desktop.api2.search_entities_interactive'),
]

# Default Configurations
dynamic_patterns += [
  url(r'^desktop/api/configurations/?$', 'desktop.configuration.api.default_configurations'),
  url(r'^desktop/api/configurations/user/?$', 'desktop.configuration.api.app_configuration_for_user'),
  url(r'^desktop/api/configurations/delete/?$', 'desktop.configuration.api.delete_default_configuration'),
]

dynamic_patterns += [url(r'^desktop/api/users/autocomplete', 'useradmin.views.list_for_autocomplete')]

# Metrics specific
if METRICS.ENABLE_WEB_METRICS.get():
  dynamic_patterns += [url(r'^desktop/metrics/', include('desktop.lib.metrics.urls')]

dynamic_patterns += [url(r'^admin/', include(admin.site.urls)]

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
      dynamic_patterns.extend( patterns('', ('^' + re.escape(app.name) + '/', include(app.urls, **namespace))) )
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
