#!/usr/bin/env bash
set -e

CONFIG="/tmp/config/ckan.ini"

if [ ! -s "$CONFIG" ]; then
	echo "$CONFIG not found; Exiting" >&2
	exit 1
fi

# values in req_env_vars will be checked for existence; if check fails, deployment is aborted
req_env_vars=(SOLR_HOST SOLR_PORT DATAPUSHER_HOST DATAPUSHER_PORT)

#check needed env before doing anything
missing_req=0
for var in ${req_env_vars[@]}
do
    if [ "x"$(eval echo "\$$var") = "x" ]; then
		if [ $missing_req -eq 0 ]; then
			missing_req=1
			echo "ERROR: One or more needed environment variables not set" >&2
		fi
		echo "\$$var is empty"
	fi
done
if [ $missing_req -eq 1 ]; then
	echo "ABORTING" >&2
  exit 1
fi

while [[ $(curl -LI "http://${SOLR_HOST}:${SOLR_PORT}/solr/ckan/select/?q=%2A%3A%2A&rows=1&wt=json" -o /dev/null -w '%{http_code}\n' -s) != "200" ]]; do
    echo "Waiting for SOLR..."
    sleep 2
done

while [[ $(curl -LI "http://${DATAPUSHER_HOST}:${DATAPUSHER_PORT}/" -o /dev/null -w '%{http_code}\n' -s) != "200" ]]; do
    echo "Waiting for DATAPUSHER..."
    sleep 2
done

# Set the common uwsgi options
UWSGI_OPTS="--gevent 2000 --gevent-early-monkey-patch"
uwsgi --ini /etc/ckan/uwsgi.ini ${UWSGI_OPTS}
