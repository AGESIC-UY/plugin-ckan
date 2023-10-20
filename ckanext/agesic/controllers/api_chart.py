# coding=utf-8
import json
import logging

from flask import make_response
from sqlalchemy.sql import text

import ckan.authz as authz
from ckan.common import g, _
from ckan.model import Package, Session

log = logging.getLogger(__name__)


class ApiChartController:

    def __get_response(self, data={}):
        response = make_response()
        response.headers['Content-Type'] = 'application/json'
        response.data = json.dumps(data)
        return response

    @staticmethod
    def __get_query_package_by_field(field='state', field_value='active', type='dataset', subquery='', additional=''):
        return """SELECT COUNT(DISTINCT package.id) FROM package
                                {0}
                                WHERE package.{1} = '{2}'
                                    AND package.type = '{3}'
                                    {4}
                                """.format(subquery, field, field_value, type, additional)

    def __get_query_count_by_field(self, field='state', field_value='active', type='dataset', subquery='', additional=''):
        connection = Session.connection()
        return connection.execute((self.__get_query_package_by_field(field=field,
                                                                          field_value=field_value,
                                                                          type=type,
                                                                          subquery=subquery,
                                                                          additional=additional))).fetchone()[0]

    @staticmethod
    def __get_query_resources_by_field(field='state', field_value='active', subquery='', additional=''):
        return """SELECT COUNT(DISTINCT resource.id) FROM resource
                                {0}
                                WHERE resource.{1} = '{2}'
                                    {3}
                                """.format(subquery, field, field_value, additional)

    def __get_query_resources_count_by_field(self, field='state', field_value='active', subquery='', additional=''):
        connection = Session.connection()
        return connection.execute((self.__get_query_resources_by_field(field=field,
                                                                            field_value=field_value,
                                                                            subquery=subquery,
                                                                            additional=additional))).fetchone()[0]

    @staticmethod
    def __get_query_package_by_year(date_field='metadata_created', type='dataset'):
        return """SELECT extract(year from package.{0}) as year, count(*) FROM package
                            WHERE package.{0} is not null 
                                AND package.state = 'active'
                                AND package.type = '{1}'
                            GROUP BY year
                            ORDER BY year""".format(date_field, type)

    def __get_package_by_year(self, date_field='metadata_created', type='dataset'):
        connection = Session.connection()
        return connection.execute(text(self.__get_query_package_by_year(date_field=date_field,
                                                                             type=type))).fetchall()

    @staticmethod
    def __get_query_resources_by_year(date_field='created'):
        return """SELECT extract(year from resource.{0}) as year, count(*) FROM resource
                            WHERE resource.{0} is not null
                                AND resource.state = 'active'
                            GROUP BY year
                            ORDER BY year""".format(date_field)

    @staticmethod
    def __get_array_group_by_year(label1, arr1):
        result = []
        for r in arr1:
            result.append({"Year": int(r.year), label1: int(r.count)})
        return result

    @staticmethod
    def __get_query_resources_by_url(field):
        return """SELECT {0} as field, count(*) FROM resource
                    WHERE resource.state = 'active'
                    GROUP BY {0}
                    ORDER BY count(*) DESC
                    """.format(field)

    @staticmethod
    def __get_query_resources_package_by_field(field):
        return """SELECT {0} as field, count(*) FROM resource
                        INNER JOIN package ON package.id = resource.package_id
                        WHERE resource.state = 'active' AND package.state = 'active'
                        GROUP BY {0}
                        ORDER BY count(*) DESC
                        """.format(field)

    def __get_datasets_total(self):
        datasets_active = self.__get_query_count_by_field(additional='AND private is False')
        datasets_private = self.__get_query_count_by_field(additional='AND private is True')
        datasets_draft = self.__get_query_count_by_field(field_value="draft")
        datasets_created = datasets_active + datasets_draft
        subquery_categories = " INNER JOIN member ON member.table_id = package.id AND member.table_name = 'package' " \
                              "INNER JOIN \"group\" ON \"group\".type = 'group' AND member.group_id = \"group\".id "
        additional_categories = " AND member.state = 'active' AND private is False"
        datasets_with_categories = self.__get_query_count_by_field(subquery=subquery_categories,
                                                                   additional=additional_categories)
        subquery_transparencia = " INNER JOIN package_tag on package.id = package_tag.package_id " \
                                 "INNER JOIN tag t on package_tag.tag_id = t.id AND package_tag.state = 'active' "
        additional_transparencia = " AND ((t.name = 'Transparencia Activa' AND private is False) " \
                                    "OR (t.name = 'Transparencia activa' AND private is False)) "
        datasets_with_transparencia = self.__get_query_count_by_field(subquery=subquery_transparencia,
                                                                      additional=additional_transparencia)

        result = [{"Type": 'Publicados',
                   "Count": datasets_active},
                  {"Type": 'Transparencia activa',
                   "Count": datasets_with_transparencia},
                  {"Type": 'Sin categorías',
                   "Count": datasets_active - datasets_with_categories}]
        if g.user and authz.is_sysadmin(g.user):
            result.extend([{"Type": 'Privados',
                            "Count": datasets_private},
                           {"Type": 'En borradores',
                            "Count": datasets_draft}])
        return result

    def __get_showcases_total(self):
        showcase_active = self.__get_query_count_by_field(type='showcase', additional='AND private is False')
        showcase_draft = self.__get_query_count_by_field(field_value="draft",  type='showcase')
        showcase_created = showcase_active + showcase_draft

        result = [{"Type": 'Publicadas',
                   "Count": self.__get_query_count_by_field(type='showcase', additional='AND private is False')}]
        if g.user and authz.is_sysadmin(g.user):
            result.extend([{"Type": 'Privadas',
                            "Count": self.__get_query_count_by_field(type='showcase', additional='AND private is True')},
                           {"Type": 'En borradores',
                            "Count": showcase_draft}])
        return result

    def __get_resources_total(self):
        connection = Session.connection()
        arr1 = connection.execute(text(self.__get_query_resources_package_by_field('package.license_id'))).fetchall()
        with_license = 0
        lics = {}
        for desc, id in Package.get_license_options():
            lics[id] = desc
        for r in arr1:
            if lics[r.field]:
                with_license = with_license + int(r.count)
        result = [{"Type": 'Publicados',
                   "Count": self.__get_query_resources_count_by_field()},
                  {"Type": 'Locales',
                   "Count": self.__get_query_resources_count_by_field(additional=" AND url_type = 'upload'")},
                  {"Type": 'Externos',
                   "Count": self.__get_query_resources_count_by_field(additional=" AND (url_type != 'upload' or url_type is null)")},
                  {"Type": 'Con licencia',
                   "Count": with_license}]
        return result

    def __get_organization_total(self):
        query = "SELECT g.title AS organization,count(DISTINCT p.id) AS datasets, " \
                "count(r.id) AS resources, max(r.created) AS last_resource_created " \
                "FROM \"group\" g " \
                "LEFT JOIN package p ON g.id = p.owner_org AND p.state = 'active' " \
                "LEFT JOIN resource r ON p.id = r.package_id AND r.state = 'active' " \
                "WHERE g.type = 'organization' AND g.state = 'active' " \
                "GROUP BY g.title " \
                "ORDER BY g.title"

        connection = Session.connection()
        arr1 = connection.execute(query).fetchall()
        result = []
        for r in arr1:
            result.extend([{"Organization": r.organization,
                            "Datasets": int(r.datasets),
                            "Resources": int(r.resources),
                            "LastResource": str(r.last_resource_created)}])
        return result

    def __get_datasets_by_year(self):
        res1 = self.__get_package_by_year()
        return self.__get_array_group_by_year("Created", res1)

    def __get_showcase_by_year(self):
        res1 = self.__get_package_by_year(type='showcase')
        return self.__get_array_group_by_year("Created", res1)

    def __get_resources_by_year(self):
        connection = Session.connection()
        res1 = connection.execute(text(self.__get_query_resources_by_year())).fetchall()
        return self.__get_array_group_by_year("Created", res1)

    ##############
    # Endpoints
    ##############

    def chart_datasets_enabled(self):
        return self.__get_response(self.__get_datasets_by_year())

    def table_datasets_total(self):
        return self.__get_response(self.__get_datasets_total())

    def chart_showcases_enabled(self):
        return self.__get_response(self.__get_showcase_by_year())

    def table_showcases_total(self):
        return self.__get_response(self.__get_showcases_total())

    def chart_resources_enabled(self):
        return self.__get_response(self.__get_resources_by_year())

    def table_resources_total(self):
        return self.__get_response(self.__get_resources_total())

    def resources_by_format(self):
        connection = Session.connection()
        arr1 = connection.execute(text(self.__get_query_resources_by_url('format'))).fetchall()
        result = []
        for r in arr1:
            result.extend([{"Type": r.field, "Count": int(r.count)}])
        return self.__get_response(result)

    def resources_by_license(self):
        connection = Session.connection()
        arr1 = connection.execute(text(self.__get_query_resources_package_by_field('package.license_id'))).fetchall()
        result = []
        lics = {}
        for desc, id in Package.get_license_options():
            lics[id] = desc
        for r in arr1:
            result.extend([{"Type": lics[r.field], "Count": int(r.count)}])
        return self.__get_response(result)

    def table_organizations_total(self):
        return self.__get_response(self.__get_organization_total())
