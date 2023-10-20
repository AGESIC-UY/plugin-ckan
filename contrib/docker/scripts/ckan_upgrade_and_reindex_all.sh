#!/usr/bin/env bash
set -e
cd /tmp/config/
echo "Upgrade CKAN database"
ckan -c /tmp/config/ckan.ini db upgrade
echo "Rebuild search index"
ckan -c /tmp/config/ckan.ini search-index rebuild --force
echo "Migrate package activity"
python /usr/lib/ckan/default/src/ckan/ckan/migration/migrate_package_activity.py -c /tmp/config/ckan.ini --delete yes
