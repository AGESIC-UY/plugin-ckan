import logging

from flask import Blueprint
import ckan.lib.base as base
from ckanext.agesic.utils import resource_health

log = logging.getLogger(__name__)


def custom_content1():
    # Ayudanos a mejorar
    return base.render('agesic/custom_content1.html')


def custom_content2():
    # Preguntas frecuentes
    return base.render('agesic/custom_content2.html')


def custom_panel():
    return base.render('agesic/custom_panel.html')


def custom_accessibility():
    return base.render('agesic/custom_accessibility.html')

agesic_public_blueprint = Blueprint(u'agesic_public_blueprint', __name__, url_prefix='/agesic/portal')
agesic_public_blueprint.add_url_rule(u'/feedback', 'custom_content1', view_func=custom_content1)
agesic_public_blueprint.add_url_rule(u'/faq', 'custom_content2', view_func=custom_content2)
agesic_public_blueprint.add_url_rule(u'/panel', 'panel', view_func=custom_panel)
agesic_public_blueprint.add_url_rule(u'/accesibilidad', 'custom_accessibility', view_func=custom_accessibility)
agesic_public_blueprint.add_url_rule(u'/js/resource_health_and_status/<resource_id>', 'resource_health_and_status',
                                     view_func=resource_health)
