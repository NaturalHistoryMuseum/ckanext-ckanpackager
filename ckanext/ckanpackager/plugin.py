# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

from ckanext.ckanpackager import routes, cli
from ckanext.ckanpackager.lib.helpers import get_format_options
from ckanext.ckanpackager.lib.utils import url_for_package_resource
from ckanext.ckanpackager.logic import action, auth


class CkanPackagerPlugin(SingletonPlugin):
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)
    implements(interfaces.IActions)
    implements(interfaces.IAuthFunctions)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IClick)

    def configure(self, app_cfg):
        """
        Implementation of IConfigurable.configure.

        :param app_cfg: config dictionary
        """
        # As per ckan.controllers.packager.resource_read - there is no API for getting this
        site_url = app_cfg.get('ckan.site_url', '').rstrip('/')
        app_cfg['datastore_api'] = f'{site_url}/api/action'

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'url_for_package_resource': url_for_package_resource,
            'get_format_options': get_format_options,
        }

    # IConfigurer
    def update_config(self, app_config):
        """
        Add our template directory.

        :param app_config:
        """
        toolkit.add_template_directory(app_config, 'theme/templates')
        toolkit.add_resource('theme/assets', 'ckanext-ckanpackager')

    # IActions
    def get_actions(self):
        return {
            'packager_stats': action.packager_stats,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'packager_stats': auth.packager_stats,
        }
