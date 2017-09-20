from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-ckanpackager',
	version=version,
	description="CKAN extension to provide resource downloads using ckanpackager",
	url='https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager',
	packages=find_packages(),
	namespace_packages=['ckanext', 'ckanext.ckanpackager'],
	entry_points="""
	[ckan.plugins]
	ckanpackager = ckanext.ckanpackager.plugin:CkanPackagerPlugin
	[paste.paster_command]
	initdb=ckanext.ckanpackager.commands.initdb:CKANPackagerCommand
	""",
)

