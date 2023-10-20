#!/usr/bin/env bash
set -e
pip3 install --upgrade --no-cache-dir pip

cd $CKAN_VENV/src/
BRANCH_NAME="ckan-2.9.8-agesic"

echo "Copying default config"
cp -v $CKAN_VENV/src/ckanext-agesic/contrib/docker/config/ckan/who.ini $CKAN_CONFIG/who.ini
cp -v $CKAN_VENV/src/ckanext-agesic/contrib/docker/config/ckan/ckan.ini $CKAN_CONFIG/ckan.ini
cp -v $CKAN_VENV/src/ckanext-agesic/contrib/docker/config/uwsgi/uwsgi.ini $CKAN_CONFIG/uwsgi.ini

pip3 install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirement-setuptools.txt
pip3 install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirements.txt
pip3 install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/dev-requirements.txt
cd $CKAN_VENV/src/ckan/ && python3 setup.py install

cd $CKAN_VENV/src/
echo -e "\n\n*************************************\n\n"
echo "Cloning projects"


DIRS="
ckanext-basiccharts
ckanext-dcat
ckanext-geoview
ckanext-googleanalytics
ckanext-harvest
ckanext-iduruguay
ckanext-pdfview
ckanext-qa
ckanext-repo
ckanext-report
ckanext-archiver
ckanext-showcase
ckanext-agesic
ckan
"
for DIR in $DIRS; do
  cd $CKAN_VENV/src/
  echo -e "\n\n*************************************\n\n"
  echo "Processing folder $DIR"
  cd /usr/lib/ckan/default/src/$DIR
  echo -e "Processing branch $(git rev-parse --abbrev-ref HEAD) \n"
  if [[ DIR == "ckan" ]]; then
    if test -f "dev-requirements.txt"; then
      echo "Installing dev-requirements"
      pip3 install --no-cache-dir -r dev-requirements.txt
    fi
  fi
  if test -f "pip-requirements.txt"; then
    echo "Installing pip-requirements"
    pip3 install --no-cache-dir -r pip-requirements.txt
  fi
  if test -f "requirements-py3.txt"; then
    echo "Installing requirements-py3.txt"
    pip3 install --no-cache-dir -r requirements-py3.txt
  elif test -f "requirements.txt"; then
    echo "Installing requirements"
    pip3 install --no-cache-dir -r requirements.txt
  fi
  echo "Installing $DIR"
  python3 setup.py develop
done
