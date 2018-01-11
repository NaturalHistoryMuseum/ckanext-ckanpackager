import urlparse
import ckan.plugins.toolkit as t


class NotADownloadableResource(Exception):
    '''Exception raised when the given resource is not a downloadable resource'''
    pass


def is_downloadable_resource(resource_id):
    '''Returns True if the resource can be downloaded - either because it is in the datastore or we have a URL link
    to it.

    @param resource_id: Resource id
    @raises ckan.plugins.toolkit.ObjectNotFound: If the resource does not exist
    @returns: True or False
    '''
    resource = t.get_action(u'resource_show')(None, {u'id': resource_id})
    return resource.get(u'datastore_active', False) or resource.get(u'url', False)


def url_for_package_resource(package_id, resource_id, anon=True, use_request=True, extra_filters=None):
    '''Given a resource_id, return the URL for packaging that resource

    Will return an empty URL if the resource exists but is not downloadable.

    @package_id: The package id
    @param resource_id: The resource id
    @param anon: If True, will add 'anon=1' to the query string *if* this is an anonymous request
    @param use_request: If True (default) include the filters of the current request
    @param extra_filters: Extra filters (on top of those in the request URL) to add to the link
    @raises ckan.plugins.toolkit.ObjectNotFound: If the resource does not exist
    @return: The URL for the action.
    '''
    if use_request:
        get = dict(t.request.GET)
    else:
        get = {}

    filters = []
    if u'filters' in get:
        filters = get[u'filters'].split(u'|')
    if extra_filters:
        filters += [u'%s:%s' % (k, v) for (k, v) in extra_filters.items()]
    if filters:
        get[u'filters'] = u'|'.join(filters)

    get[u'resource_id'] = resource_id
    get[u'package_id'] = package_id
    get[u'destination'] = t.request.url
    if anon and not t.c.user:
        get[u'anon'] = u'1'

    resource = t.get_action(u'resource_show')(None, {u'id': resource_id})
    if not resource.get(u'datastore_active', False):
        if resource.get(u'url', False):
            get[u'resource_url'] = resource.get(u'url')
        else:
            return u''

    return t.url_for(u'package_resource', **get)


def url_for_resource_page(package_id, resource_id):
    '''Helper function to return the URL of a resource page

    @param resource_id: Resource id
    @raises ckan.plugins.toolkit.ObjectNotFound: If the resource does not exist
    @return: The URL for the resource
    '''
    return t.url_for(controller=u'package',
                     action=u'resource_read',
                     id=package_id,
                     resource_id=resource_id)


def redirect_to(destination, **kw):
    '''Wrapper around ckan.plugins.toolkit.redirect_to which accepts a base url with query strings

    @param destination: Destination URL. May contain query string, etc.
    @param **kw: Addition arguments that get added to the query string
    '''
    parts = urlparse.urlparse(destination)
    dest_base = urlparse.urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, u'', u''))
    new_kw = dict(urlparse.parse_qs(parts.query))
    for k, v in kw:
        if k in new_kw:
            new_kw.append(v)
        else:
            new_kw[k] = v
    t.redirect_to(dest_base.encode(u'utf8'), **new_kw)
