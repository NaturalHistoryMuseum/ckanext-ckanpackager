<!--notices-start-->
> **Warning**
> ## Version 3 of ckanext-ckanpackager will remove support for ckanpackager.
>
> [ckanpackager](http://github.com/NaturalHistoryMuseum/ckanpackager) is being deprecated, and so v3 of this extension will no longer support connecting to it.
>
> **All** functionality is being removed _except for the database tables_, to allow other extensions continuing access to legacy data without having to maintain a ckanpackager instance.
>
> If you are still using ckanpackager and wish to use this extension with your instance, you will have to use v2 or earlier.

<!--notices-end-->

<!--header-start-->
<img src="https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager/raw/main/.github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-ckanpackager

[![Tests](https://img.shields.io/github/actions/workflow/status/NaturalHistoryMuseum/ckanext-ckanpackager/main.yml?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-ckanpackager/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-ckanpackager)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-ckanpackager?style=flat-square)](https://ckanext-ckanpackager.readthedocs.io)

_A CKAN extension that stores legacy download statistics from the deprecated service ckanpackager._

<!--header-end-->

# Overview

<!--overview-start-->
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
All configuration options have been removed.

<!--configuration-end-->

# Usage

<!--usage-start-->
## Actions

### `packager_stats`
**REMOVED**

## Commands

### `initdb`
Initialises the ckanpackager database tables.

_This command is still valid, but if you don't already have these database tables, there may not be much point._

  ```bash
  ckan -c $CONFIG_FILE ckanpackager initdb
  ```

## Templates

**REMOVED**

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
