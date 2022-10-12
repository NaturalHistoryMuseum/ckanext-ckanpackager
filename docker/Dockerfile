FROM naturalhistorymuseum/ckantest:0.1

WORKDIR /base/src/ckanext-ckanpackager

# copy over the ckanext-ckanpackager source
COPY . .

# install the dependencies
RUN python setup.py develop && \
    pip install -r requirements.txt && \
    pip install -r dev_requirements.txt

# this entrypoint ensures our service dependencies (postgresql, solr and redis) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "/opt/waits/basic.sh"]

# run the tests with coverage output
CMD ["pytest", "--cov=ckanext.ckanpackager", "--ckan-ini=test.ini", "tests"]
