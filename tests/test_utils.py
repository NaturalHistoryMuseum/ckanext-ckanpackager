from unittest.mock import patch, MagicMock

from ckanext.ckanpackager.lib.utils import is_downloadable_resource


class TestIsDownloadableResource(object):

    def test_datastore_active(self):
        resource = dict(datastore_active=True)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert is_downloadable_resource(MagicMock())

    def test_has_url(self):
        resource = dict(url='https://beans.com')
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert is_downloadable_resource(MagicMock())

    def test_datastore_inactive(self):
        resource = dict(datastore_active=False)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert not is_downloadable_resource(MagicMock())

    def test_neither(self):
        resource = dict()
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert not is_downloadable_resource(MagicMock())

    def test_datastore_inactive_but_has_url(self):
        resource = dict(datastore_active=False, url='https://beans.com')
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert is_downloadable_resource(MagicMock())

    def test_both(self):
        resource = dict(datastore_active=True, url='https://beans.com')
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.utils.toolkit', toolkit):
            assert is_downloadable_resource(MagicMock())
