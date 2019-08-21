# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckanext.ckanpackager import routes
from ckanext.ckanpackager.lib.helpers import should_show_format_options
from ckanext.ckanpackager.lib.utils import url_for_package_resource
from ckanext.ckanpackager.logic import action, auth

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

config = {}


class CkanPackagerPlugin(SingletonPlugin):
    ''' '''
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)
    implements(interfaces.IActions)
    implements(interfaces.IAuthFunctions)
    implements(interfaces.IBlueprint, inherit=True)

    def configure(self, app_cfg):
        '''Implementation of IConfigurable.configure

        :param app_cfg: config dictionary

        '''
        config[u'url'] = app_cfg.get(u'ckanext.ckanpackager.url')
        config[u'secret'] = app_cfg.get(u'ckanext.ckanpackager.secret')
        config[u'allow_anon'] = app_cfg.get(u'ckanext.ckanpackager.allow_anon', False)
        # As per ckan.controllers.packager.resource_read - there is no API for getting
        #  this.
        config[u'datastore_api'] = u'%s/api/action' % app_cfg.get(u'ckan.site_url',
                                                                  u'').rstrip('/')

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    def get_helpers(self):
        '''Implementation of ITemplateHelpers:get_helpers

        Provide a helper for create a download url from a resource id


        '''
        return {
            u'url_for_package_resource': url_for_package_resource,
            u'should_show_format_options': should_show_format_options
            }

    def update_config(self, app_config):
        '''Implementation IConfigurer.update_config

        Add our template directory

        :param app_config:

        '''
        toolkit.add_template_directory(app_config, u'theme/templates')
        toolkit.add_public_directory(config, u'theme/public')
        toolkit.add_resource(u'theme/public', u'ckanext-ckanpackager')

    # IActions
    def get_actions(self):
        return {
            u'packager_stats': action.get_packager_stats_action(config),
            }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            u'packager_stats': auth.packager_stats,
            }
