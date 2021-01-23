from ckanext.ckanpackager.lib.helpers import should_show_format_options
from mock import patch, MagicMock


class TestShouldShowFormatOptions(object):

    def test_has_datastore_active(self):
        resource = dict(datastore_active=True)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch(u'ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert should_show_format_options(MagicMock())

    def test_should_show_format_options_no(self):
        resource = dict(datastore_active=False)
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch(u'ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert not should_show_format_options(MagicMock())

    def test_should_show_format_options_missing(self):
        resource = dict()
        toolkit = MagicMock(get_action=MagicMock(return_value=MagicMock(return_value=resource)))
        with patch(u'ckanext.ckanpackager.lib.helpers.toolkit', toolkit):
            assert not should_show_format_options(MagicMock())
