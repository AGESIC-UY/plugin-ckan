FROM solr:6.6.2
MAINTAINER Open Knowledge

# Enviroment
ENV SOLR_CORE ckan

# Create Directories
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/conf
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/data

# Adding Files
ADD ./contrib/docker/config/solr/solrconfig.xml \
./contrib/docker/config/solr/schema.xml \
./contrib/docker/config/solr/currency.xml \
./contrib/docker/config/solr/synonyms.txt \
./contrib/docker/config/solr/stopwords.txt \
./contrib/docker/config/solr/protwords.txt \
./contrib/docker/config/solr/elevate.xml \
/opt/solr/server/solr/$SOLR_CORE/conf/

# Create Core.properties
RUN echo name=$SOLR_CORE > /opt/solr/server/solr/$SOLR_CORE/core.properties

# Giving ownership to Solr
USER root
ADD ./contrib/docker/config/solr/uid_entrypoint.sh /docker-entrypoint-initdb.d/
ENV SOURCE_DIR /opt/solr/server/
RUN chmod -R u+x ${SOURCE_DIR} && \
    chgrp -R 0 ${SOURCE_DIR} && \
    chmod -R g=u ${SOURCE_DIR} /etc/passwd

USER solr
