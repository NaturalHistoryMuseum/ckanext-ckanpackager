# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckanext.ckanpackager import routes, cli
from ckanext.ckanpackager.lib.helpers import should_show_format_options
from ckanext.ckanpackager.lib.utils import url_for_package_resource
from ckanext.ckanpackager.logic import action, auth

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit


class CkanPackagerPlugin(SingletonPlugin):
    ''' '''
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)
    implements(interfaces.IActions)
    implements(interfaces.IAuthFunctions)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IClick)

    def configure(self, app_cfg):
        '''Implementation of IConfigurable.configure

        :param app_cfg: config dictionary

        '''
        # As per ckan.controllers.packager.resource_read - there is no API for getting
        #  this.
        app_cfg[u'datastore_api'] = u'%s/api/action' % app_cfg.get(u'ckan.site_url',
                                                                  u'').rstrip('/')

    ## IClick
    def get_commands(self):
        return cli.get_commands()

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
        toolkit.add_resource(u'theme/assets', u'ckanext-ckanpackager')

    # IActions
    def get_actions(self):
        return {
            u'packager_stats': action.packager_stats,
            }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            u'packager_stats': auth.packager_stats,
            }
