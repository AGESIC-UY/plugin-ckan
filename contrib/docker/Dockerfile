# Based in Ckan examples, see CKAN docs on installation from Docker Compose on usage
FROM python:3.9-slim-bullseye
MAINTAINER Adrian Quintero

# Set timezone
ENV TZ=America/Montevideo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Setting the locale
ENV LC_ALL=en_US.UTF-8

# Define environment variables
ENV CKAN_HOME /usr/lib/ckan
ENV CKAN_VENV $CKAN_HOME/default
ENV CKAN_CONFIG /etc/ckan
ENV CKAN_STORAGE_PATH=/var/lib/ckan/default
ENV CKAN_ARCHIVE_PATH=$CKAN_STORAGE_PATH/archive
ENV CKAN_INI=/tmp/config/ckan.ini

# Build-time variables specified by docker-compose.yml / .env
ARG CKAN_SITE_URL
ENV BRANCH_NAME="ckan-2.9.8-agesic"

# Setup virtual environment for CKAN
RUN mkdir -p $CKAN_VENV/src $CKAN_CONFIG $CKAN_STORAGE_PATH $CKAN_ARCHIVE_PATH

RUN apt -y update
RUN apt -q -y install git

# Install required system packages
RUN bash $CKAN_VENV/src/ckanext-agesic/contrib/docker/scripts/install_dependencies.sh

# Setup CKAN
COPY . $CKAN_VENV/src/

RUN bash $CKAN_VENV/src/ckanext-agesic/contrib/docker/scripts/install_plugins_2.9.3.sh

### UWSGI ###
RUN UWSGI_PROFILE_OVERRIDE=ssl=false pip3 install --upgrade --no-cache-dir uwsgi==2.0.22 gevent==22.10.2 greenlet==2.0.2
### UWSGI ###

WORKDIR $CKAN_VENV/src/ckan

RUN chmod -R u+x ${CKAN_VENV} && \
    chgrp -R 0 ${CKAN_VENV} && \
    chmod -R g=u ${CKAN_VENV} /etc/passwd

EXPOSE 5000
USER 10001

ENTRYPOINT [ "/usr/lib/ckan/default/src/ckanext-agesic/contrib/docker/scripts/uid_entrypoint.sh" ]
CMD "/usr/lib/ckan/default/src/ckanext-agesic/contrib/docker/scripts/start_ckan.sh"
