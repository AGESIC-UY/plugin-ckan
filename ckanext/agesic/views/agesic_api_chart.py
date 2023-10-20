import logging
from flask import Blueprint
from ckanext.agesic.controllers.api_chart import ApiChartController

log = logging.getLogger(__name__)


chart = ApiChartController()

agesic_api_chart_blueprint = Blueprint(u'agesic_api_chart_blueprint', __name__, url_prefix='/agesic/charts')
agesic_api_chart_blueprint.add_url_rule(u'/chart_datasets_enabled', 'chart_datasets_enabled',
                                        view_func=chart.chart_datasets_enabled)
agesic_api_chart_blueprint.add_url_rule(u'/table_datasets_total', 'table_datasets_total',
                                        view_func=chart.table_datasets_total)
agesic_api_chart_blueprint.add_url_rule(u'/chart_showcases_enabled', 'chart_showcases_enabled',
                                        view_func=chart.chart_showcases_enabled)
agesic_api_chart_blueprint.add_url_rule(u'/table_showcases_total', 'table_showcases_total',
                                        view_func=chart.table_showcases_total)
agesic_api_chart_blueprint.add_url_rule(u'/chart_resources_enabled', 'chart_resources_enabled',
                                        view_func=chart.chart_resources_enabled)
agesic_api_chart_blueprint.add_url_rule(u'/table_resources_total', 'table_resources_total',
                                        view_func=chart.table_resources_total)
agesic_api_chart_blueprint.add_url_rule(u'/resources_by_format', 'resources_by_format',
                                        view_func=chart.resources_by_format)
agesic_api_chart_blueprint.add_url_rule(u'/resources_by_license', 'resources_by_license',
                                        view_func=chart.resources_by_license)
agesic_api_chart_blueprint.add_url_rule(u'/table_organizations_total', 'table_organizations_total',
                                        view_func=chart.table_organizations_total)
