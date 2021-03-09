from ckan.plugins import toolkit


def packager_stats(context, data_dict):
    resource_id = data_dict.get('resource_id', None)
    if resource_id is not None:
        return True
    else:
        return toolkit.check_access('resource_show', context, {'id': resource_id})
