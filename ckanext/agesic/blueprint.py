# encoding: utf-8
import logging

from ckanext.agesic.views.agesic_admin import agesic_admin_blueprint
from ckanext.agesic.views.agesic_api_chart import agesic_api_chart_blueprint
from ckanext.agesic.views.agesic_public import agesic_public_blueprint
from ckanext.agesic.views.agesic_user import agesic_user_blueprint
from ckanext.agesic.views.agesic_api_pentaho import agesic_api_pentaho_blueprint


log = logging.getLogger(__name__)


def get_blueprints():
    return [agesic_admin_blueprint, agesic_api_chart_blueprint, agesic_public_blueprint, agesic_user_blueprint,
            agesic_api_pentaho_blueprint]
