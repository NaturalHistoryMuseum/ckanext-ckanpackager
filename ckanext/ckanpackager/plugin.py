# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckanext.ckanpackager.lib.helpers import should_show_format_options
from ckanext.ckanpackager.lib.utils import url_for_package_resource

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

config = {}


class CkanPackagerPlugin(SingletonPlugin):
    ''' '''
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IRoutes, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)

    def configure(self, app_cfg):
        '''Implementation of IConfigurable.configure

        :param app_cfg: config dictionary

        '''
        config[u'url'] = app_cfg[u'ckanpackager.url']
        config[u'secret'] = app_cfg[u'ckanpackager.secret']
        config[u'allow_anon'] = app_cfg.get(u'ckanpackager.allow_anon', False)
        # As per ckan.controllers.packager.resource_read - there is no API for getting
        #  this.
        config[u'datastore_api'] = u'%s/api/action' % app_cfg.get(u'ckan.site_url',
                                                                  u'').rstrip('/')

    def get_helpers(self):
        '''Implementation of ITemplateHelpers:get_helpers
        
        Provide a helper for create a download url from a resource id


        '''
        return {
            u'url_for_package_resource': url_for_package_resource,
            u'should_show_format_options': should_show_format_options
            }

    def before_map(self, map_route):
        '''Implements Iroutes.before_map
        
        Add our custom download action

        :param map_route: 

        '''
        map_route.connect(u'package_resource',
                          '/dataset/{package_id}/resource/{resource_id}/package',
                          controller=u'ckanext.ckanpackager.controllers.packager'
                                     u':CkanPackagerController',
                          action=u'package_resource')
        return map_route

    def update_config(self, app_config):
        '''Implementation IConfigurer.update_config
        
        Add our template directory

        :param app_config: 

        '''
        toolkit.add_template_directory(app_config, u'theme/templates')
        toolkit.add_public_directory(config, u'theme/public')
        toolkit.add_resource(u'theme/public', u'ckanext-ckanpackager')
