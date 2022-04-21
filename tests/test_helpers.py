from ckanext.ckanpackager.lib.helpers import get_format_options
from unittest.mock import patch, MagicMock


class TestGetFormatOptions:

    def test_datastore_active(self):
        resource = dict(datastore_active=True)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert get_format_options(MagicMock()) == ['CSV', 'TSV', 'XLSX']

    def test_datastore_active_dwc(self):
        resource = dict(datastore_active=True, format='dwc')
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert get_format_options(MagicMock()) == ['CSV', 'TSV']

    def test_datastore_inactive(self):
        resource = dict(datastore_active=False)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert get_format_options(MagicMock()) == []

    def test_datastore_inactive_missing(self):
        resource = dict()
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch('ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert get_format_options(MagicMock()) == []
