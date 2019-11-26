from ckan.plugins import toolkit


def packager_stats(context, data_dict):
    resource_id = data_dict.get(u'resource_id', None)
    if resource_id is not None:
        return True
    else:
        return toolkit.check_access(u'resource_show', context, {u'id': resource_id})
