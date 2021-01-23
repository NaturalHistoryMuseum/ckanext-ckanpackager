FROM openknowledge/ckan-dev:2.9-py2

# ckan is installed in /srv/app/src/ckan in the ckan-dev image we're basing this image on
WORKDIR /srv/app/src/ckanext-ckanpackager

# copy over the ckanext-ckanpackager source
COPY . .

# might as well update pip while we're here!
RUN pip install --upgrade pip

# fixes this https://github.com/ckan/ckan/issues/5570
RUN pip install pytest-ckan

# install the dependencies
RUN python setup.py develop && \
    pip install -r requirements.txt && \
    pip install -r dev_requirements.txt

# this entrypoint ensures our service dependencies (postgresql, solr and redis) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "docker/entrypoint.sh"]

# run the tests with coverage output
CMD ["pytest", "--cov=ckanext.ckanpackager", "--ckan-ini=test.ini", "tests"]
