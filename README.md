<!--header-start-->
<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-ckanpackager

[![Tests](https://img.shields.io/github/workflow/status/NaturalHistoryMuseum/ckanext-ckanpackager/Tests?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-ckanpackager/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-ckanpackager)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-ckanpackager?style=flat-square)](https://ckanext-ckanpackager.readthedocs.io)

_A CKAN extension that provides a user interface to download resources with [ckanpackager](http://github.com/NaturalHistoryMuseum/ckanpackager)._

<!--header-end-->

# Overview

<!--overview-start-->
**This extension will not work without [ckanpackager](http://github.com/NaturalHistoryMuseum/ckanpackager).**

Ckanpackager is a stand-alone service that can be instructed to fetch data on a [CKAN](http://ckan.org) site using the datastore API, pack the data in a ZIP file and email the link to a given address. See the [ckanpackager github page](http://github.com/NaturalHistoryMuseum/ckanpackager) for more information.

The extension provides an HTML snippet that can be used to replace the Download button on resources. The new button will:
- Provide an overlay explaining the link will be sent later on;
- Provide a form for users to enter the destination email address;
- On resource pages, the button will ensure that currently applied filters and searches are forwarded on to the ckanpackager service.

This extension uses a database table in the CKAN database to store stats about packaging events.

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

## Installing from PyPI

```shell
pip install ckanext-ckanpackager
```

## Installing from source

1. Clone the repository into the `src` folder:
   ```shell
   cd $INSTALL_FOLDER/src
   git clone https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager.git
   ```

2. Activate the virtual env:
   ```shell
   . $INSTALL_FOLDER/bin/activate
   ```

3. Install via pip:
   ```shell
   pip install $INSTALL_FOLDER/src/ckanext-ckanpackager
   ```

### Installing in editable mode

Installing from a `pyproject.toml` in editable mode (i.e. `pip install -e`) requires `setuptools>=64`; however, CKAN 2.9 requires `setuptools==44.1.0`. See [our CKAN fork](https://github.com/NaturalHistoryMuseum/ckan) for a version of v2.9 that uses an updated setuptools if this functionality is something you need.

## Post-install setup

1. Add 'ckanpackager' to the list of plugins in your `$CONFIG_FILE`:
   ```ini
   ckan.plugins = ... ckanpackager
   ```

2. Install `lessc` globally:
   ```shell
   npm install -g "less@~4.1"
   ```

3. Initialise the database table:
   ```shell
   ckan -c $CONFIG_FILE ckanpackager initdb
   ```

<!--installation-end-->

# Configuration

<!--configuration-start-->
There are two options that _must_ be specified in your .ini config file.

## **[REQUIRED]**

| Name                  | Description                                  | Options |
|-----------------------|----------------------------------------------|---------|
| `ckanpackager.url`    | URL to the ckanpackager endpoint             |         |
| `ckanpackager.secret` | Shared secret with the ckanpackager instance |         |

<!--configuration-end-->

# Usage

<!--usage-start-->
## Actions

### `packager_stats`
Provides statistical information about the download requests made to the packager. All of the items in the `data_dict` are optional.

```python
from ckan.plugins import toolkit

data_dict = {
                'resource_id': RESOURCE_ID,
                'offset': 0,
                'limit': 100,
                'email': REQUESTER_EMAIL
            }

toolkit.get_action('packager_stats')(
    context,
    data_dict
)
```

## Commands

### `initdb`
Initialises the ckanpackager database tables.

  ```bash
  ckan -c $CONFIG_FILE ckanpackager initdb
  ```

## Templates

Add the following snippet to templates where you want the button to appear:

```html+jinja
{% snippet 'ckanpackager/snippets/package_resource.html',
   res=res, pkg=pkg, bt_class="fas fa-download", bt_text=_('Download')
%}
```

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests. The ckan image uses the Dockerfile in the `docker/` folder.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images:
   ```shell
   docker-compose build
   ```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
   ```shell
   docker-compose run ckan
   ```

<!--testing-end-->
