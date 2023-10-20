#!/usr/bin/env bash
set -e

CONFIG_TEMPLATE="/etc/ckan"
CONFIG="${CKAN_INI:-/tmp/config/ckan.ini}"

if [ ! -s "$CONFIG_TEMPLATE/ckan.ini" ]; then
	echo "$CONFIG_TEMPLATE not found; Exiting" >&2
	exit 1
fi

echo "Copying files in $CONFIG_TEMPLATE to /tmp/config/" >&2
mkdir -p /tmp/config/
cp "$CONFIG_TEMPLATE/who.ini" /tmp/config/
cp "$CONFIG_TEMPLATE/ckan.ini" /tmp/config/
cp "$CONFIG_TEMPLATE/uwsgi.ini" /tmp/config/
cp /usr/lib/ckan/default/src/ckan/wsgi.py /tmp/config/

# values in req_env_vars will be checked for existence; if check fails, deployment is aborted
req_env_vars=(PG_USER PG_PASSWORD POSTGRES_HOST PG_DATABASE SOLR_HOST SOLR_PORT REDIS_HOST REDIS_PORT \
        DATAPUSHER_HOST DATAPUSHER_PORT PG_DATASTORE_DB PG_DATASTORE_RO_USER PG_DATASTORE_RO_PASS)

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

# since all ckan vars are present on env, get entire env and try substitute everything with sed
echo "---> Update $CONFIG based on env vars"
all_env=($(env | cut -d '=' -f 1))
for var in ${all_env[@]}
do
	# will just use the env vars that contain upper-case letters, numbers and _
	var=$(echo $var | sed -n "s|[A-Z][[A-Z0-9]_]*|&|p")
	if [ ${#var} -eq 0 ]; then
		continue
	fi
	val=$(eval echo "\$$var")
	sed -i "s|\$$var|$val|g" "$CONFIG"
done

echo "---> CKAN will be started with the configuration below:"
cat "$CONFIG"
echo "---> END $CONFIG"
