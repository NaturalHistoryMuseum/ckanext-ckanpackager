import os
import requests
from ckan import plugins, logic

# we only allow a certain set of request parameters. These are the ones accepted by the
# ckanpackager's statistics/requests endpoint, minus the secret
ALLOWED_PARAMS = {
    u'offset',
    u'limit',
    u'resource_id',
    u'email'
}


def get_packager_stats_action(config):
    """
    Returns the packager_stats action function. This odd function returning the actual action
    function structure is necessary because the config lives in the plugin module so by importing it
    to here we create a circular dependency. The other option would be to import it inside the
    packager_stats function itself or move the action into the plugin module but neither of those
    felt like satisfactory ways of getting the job done. Personally, this feels slightly better,
    make of that what you will and feel free to change it if there's a neater way of doing it!

    :param config: the config object
    :return: the packager_stats action function
    """
    @logic.side_effect_free
    def packager_stats(context, data_dict):
        '''
        Provides statistical information about the download requests made to the packager.

        The options provided in the data_dict match the ones from the ckanpackager's
        /statistics/requests endpoint:

        :param offset: an offset value for pagination, defaults to 0 if not provided
        :type int: integer
        :param limit: a limit value for pagination, defaults to 100 if not provided
        :type int: integer
        :param resource_id: the id of a given resource. If provided, will filter the results to only
                            include this resource, if not provided results for all resources are
                            returned
        :type string: string
        :param email: the email address of the requester. If prodived, will filter the results to only
                      include statistics where this email was used to request the data, if not provided,
                      the results from all email addresses are returned
        :type string: string


        :returns: a list of dicts containing the statistical data. Note that the list is always ordered
                  by request time in descending order, so the first result in any response will be the
                  oldest matching result
        :rtype: list of dicts
        '''
        # check the access is appropriate
        plugins.toolkit.check_access(u'packager_stats', context, data_dict)

        # extract the parameters we're interested in from the allowed ones
        params = {key: value for key, value in data_dict.items() if key in ALLOWED_PARAMS}
        # set some defaults
        params.setdefault(u'limit', 100)
        params.setdefault(u'offset', 0)
        # create the url to post to
        url = os.path.join(config[u'url'], u'statistics', u'requests')
        # this is the data we're going to pass in the request, it has to have the secret in it
        data = {u'secret': config[u'secret']}
        # update the data we're going to send with the allowed options from the data_dict
        data.update(params)

        # make the request
        response = requests.post(url, data=data)
        # and return the data
        return response.json()

    return packager_stats
