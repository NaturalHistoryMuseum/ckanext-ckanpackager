import ckan.plugins as p
from ckanext.ckanpackager.lib.utils import url_for_package_resource

config = {}


class CkanPackagerPlugin(p.SingletonPlugin):
    p.implements(p.interfaces.ITemplateHelpers)
    p.implements(p.interfaces.IRoutes, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer)

    def configure(self, app_cfg):
        """Implementation of IConfigurable.configure

        @param app_cfg: config dictionary
        """
        config['url'] = app_cfg['ckanpackager.url']
        config['secret'] = app_cfg['ckanpackager.secret']
        config['allow_anon'] = app_cfg.get('ckanpackager.allow_anon', False)
        # As per ckan.controllers.packager.resource_read - there is no API for getting this.
        config['datastore_api'] = '%s/api/action' % app_cfg.get('ckan.site_url', '').rstrip('/')

    def get_helpers(self):
        """Implementation of ITemplateHelpers:get_helpers

        Provide a helper for create a download url from a resource id
        """
        return {
            'url_for_package_resource': url_for_package_resource
        }

    def before_map(self, map_route):
        """Implements Iroutes.before_map

        Add our custom download action"""
        map_route.connect('package_resource', '/dataset/{package_id}/resource/{resource_id}/package',
                          controller='ckanext.ckanpackager.controllers.packager:CkanPackagerController',
                          action='package_resource')
        return map_route

    def update_config(self, app_config):
        """Implementation IConfigurer.update_config

        Add our template directory
        """
        p.toolkit.add_template_directory(app_config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-ckanpackager')
