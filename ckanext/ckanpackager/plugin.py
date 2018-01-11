import ckan.plugins as p
from ckanext.ckanpackager.lib.utils import url_for_package_resource

config = {}


class CkanPackagerPlugin(p.SingletonPlugin):
    p.implements(p.interfaces.ITemplateHelpers)
    p.implements(p.interfaces.IRoutes, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer)

    def configure(self, app_cfg):
        '''Implementation of IConfigurable.configure

        @param app_cfg: config dictionary
        '''
        config[u'url'] = app_cfg[u'ckanpackager.url']
        config[u'secret'] = app_cfg[u'ckanpackager.secret']
        config[u'allow_anon'] = app_cfg.get(u'ckanpackager.allow_anon', False)
        # As per ckan.controllers.packager.resource_read - there is no API for getting this.
        config[u'datastore_api'] = u'%s/api/action' % app_cfg.get(u'ckan.site_url', u'').rstrip('/')

    def get_helpers(self):
        '''Implementation of ITemplateHelpers:get_helpers

        Provide a helper for create a download url from a resource id
        '''
        return {
            u'url_for_package_resource': url_for_package_resource
        }

    def before_map(self, map_route):
        '''Implements Iroutes.before_map

        Add our custom download action'''
        map_route.connect(u'package_resource', '/dataset/{package_id}/resource/{resource_id}/package',
                          controller=u'ckanext.ckanpackager.controllers.packager:CkanPackagerController',
                          action=u'package_resource')
        return map_route

    def update_config(self, app_config):
        '''Implementation IConfigurer.update_config

        Add our template directory
        '''
        p.toolkit.add_template_directory(app_config, u'theme/templates')
        p.toolkit.add_public_directory(config, u'theme/public')
        p.toolkit.add_resource(u'theme/public', u'ckanext-ckanpackager')
