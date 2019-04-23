import json
import os

import requests

from ckan.plugins import toolkit
from ckanext.ckanpackager.plugin import config


# we only allow a certain set of request parameters. These are the ones accepted by the
# ckanpackager's statistics/requests endpoint, minus the secret
ALLOWED_PARAMS = {
    u'offset',
    u'limit',
    u'resource_id',
    u'email'
}


def get_options_from_request():
    '''
    Filters the request parameters passed, sets defaults for offset and limit and returns as a dict.

    :return: a dict of options
    '''
    # we'll fill out the extra parameters using the query string parameters, however we want to
    # filter to ensure we only pass parameters we want to allow
    params = {key: value for key, value in toolkit.request.params.items() if key in ALLOWED_PARAMS}
    params.setdefault(u'limit', 100)
    params.setdefault(u'offset', 0)
    return params


class CkanStatsController(toolkit.BaseController):
    '''
    Controller which when requested acts as a proxy for the ckanpackager's statistics/requests
    endpoint.
    '''

    def get_stats(self):
        '''
        Retrieves the stats from the ckanpackager's statistics/requests endpoint, passing any
        allowed request parameters along too. The response is returned as JSON.

        :return: the JSON returned by the ckanpackager
        '''
        # create the url to post to
        url = os.path.join(config[u'url'], u'statistics', u'requests')
        # this is the data we're going to pass in the request, it has to have the secret in it
        data = {u'secret': config[u'secret']}
        # update the data dict with the options from the request parameters
        data.update(get_options_from_request())
        # make the request
        response = requests.post(url, data=data)
        # the return is going to be some json, set the content-type appropriately
        toolkit.response.headers[u'Content-Type'] = u'application/json'
        # and return the data
        return json.dumps(response.json())
