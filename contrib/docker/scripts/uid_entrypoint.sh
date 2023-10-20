#!/bin/sh
if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  fi
fi

if [ -f "/etc/ckan/ckan.ini" ]; then
	/usr/lib/ckan/default/src/ckanext-agesic/contrib/docker/scripts/create_config_file.sh
fi
exec "$@"
