import urlparse
import ckan.plugins.toolkit as t


class NotADatastoreResource(Exception):
    """Exception raised when the given resource is not a datastore resource"""
    pass


def is_datastore_resource(resource_id):
    """Returns True if the resource is in the datastore, false otherwise

    @param resource_id: Resource id
    @raises ckan.plugins.toolkit.ObjectNotFound: If the resource does not exist
    @returns: True or False
    """
    resource = t.get_action('resource_show')(None, {'id': resource_id})
    return resource.get('datastore_active', False)


def url_for_package_resource(package_id, resource_id, anon=True, use_request=True):
    """Given a resource_id, return the URL for packaging that resource

    @package_id: The package id
    @param resource_id: The resource id
    @param anon: If True, will add 'anon=1' to the query string *if* this is an anonymous request
    @param use_request: If True (default) include the filters of the current request
    @raises NotADatastoreResource: Raised if the resource exists but does not have data in the datastore.
    @raises ckan.logic.NotFound: If the resource doesn't exist.
    @return: The URL for the action.
    """
    if not is_datastore_resource(resource_id):
        raise NotADatastoreResource(resource_id)

    if use_request:
        get = dict(t.request.GET)
    else:
        get = {}
    get['resource_id'] = resource_id
    get['package_id'] = package_id
    get['destination'] = t.request.url
    if anon and not t.c.user:
        get['anon'] = '1'
    return t.url_for('package_resource', **get)


def url_for_resource(package_id, resource_id):
    """Helper function to return the URL of a resource

    @param resource_id: Resource id
    @raises ckan.plugins.toolkit.ObjectNotFound: If the resource does not exist
    @return: The URL for the resource
    """
    return t.url_for(controller='package',
                     action='resource_read',
                     id=package_id,
                     resource_id=resource_id)


def redirect_to(destination, **kw):
    """Wrapper around ckan.plugins.toolkit.redirect_to which accepts a base url with query strings

    @param destination: Destination URL. May contain query string, etc.
    @param **kw: Addition arguments that get added to the query string
    """
    parts = urlparse.urlparse(destination)
    dest_base = urlparse.urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, '', ''))
    new_kw = dict(urlparse.parse_qs(parts.query))
    for k, v in kw:
        if k in new_kw:
            new_kw.append(v)
        else:
            new_kw[k] = v
    t.redirect_to(dest_base.encode('utf8'), **new_kw)
