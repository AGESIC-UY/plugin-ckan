#!/bin/bash
set -e
cd /tmp/config/

echo "Tracking update"
ckan -c /tmp/config/ckan.ini tracking update

echo "Just refresh search index"
ckan -c /tmp/config/ckan.ini search-index rebuild -r --force
