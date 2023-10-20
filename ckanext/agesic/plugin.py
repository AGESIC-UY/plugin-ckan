# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
from uuid import uuid4
import jwt
import time
import logging
import urllib.request
import operator
import requests
from datetime import date, datetime, timedelta

import ckan.model as model
import ckan.logic as logic
import ckan.plugins as plugins
import ckan.lib.helpers as h

from ckan.common import config, json, c, _
from ckanext.agesic.controllers.email import SendNotificationController
from model import Session, Package, Group, ResourceView, Resource, User, Member
from plugins import toolkit as tk

from ckan import authz

from sqlalchemy.sql import select
from routes.mapper import SubMapper

from ckanext.googleanalytics import dbutil
from ckanext.agesic.utils import timestatus, get_resource_url, link_health

from ckan.logic.schema import default_extras_schema
from ckan.logic.validators import (package_id_exists,
                                   name_validator,
                                   owner_org_validator,
                                   package_name_validator,
                                   boolean_validator,
                                   email_validator,
                                   package_version_validator,
                                   clean_format,
                                   int_validator,
                                   ignore_not_sysadmin,
                                   )
from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      ignore,
                                      if_empty_same_as,
                                      unicode_safe,
                                      default,
                                      )
import ckan.lib.navl.dictization_functions as df
from ckanext.agesic.utils import UPDATE_FREQS

tk.requires_ckan_version("2.9")
from ckanext.agesic.flask_plugin import AgesicMixinPlugin

Invalid = df.Invalid

check_access = logic.check_access
get_action = logic.get_action
log = logging.getLogger(__name__)


def update_frequency_validator(value, context):
    if value is None or (hasattr(value, 'strip') and not value.strip()):
        return '-1'
    try:
        value = int_validator(value, context)
        if value not in [-1, 0, 1, 7, 15, 30, 60, 90, 182, 365, 1826]:
            raise Invalid(_('Invalid update frequency value'))
        return str(value)
    except:
        raise Invalid(_('Invalid update frequency value'))


def private_if_not_sysadmin(key, data, errors, context):
    '''Only sysadmins may pass this value'''
    from ckan.lib.navl.validators import empty
    user = context.get('user')
    ignore_auth = context.get('ignore_auth')
    log.warning("Checking value private status from request: " + str(data[key]))
    if ignore_auth or (user and authz.is_sysadmin(user)):
        log.warning("User is sysadmin, ignored permision value")
        return
    package = context.get('package')
    if package and package.state == 'active':
        if package.private == False:
            log.warning("User is not sysadmin and package is public, not updated value")
        else:
            data[key] = True
            log.warning("User is not sysadmin and package is not public, forced to private")
        return
    log.warning("Package is not active, user is not sysadmin, forced to private")
    data[key] = True


@tk.auth_allow_anonymous_access
def datastore_search(context, data_dict):
    return {'success': True}


class AgesicIDatasetFormPlugin(AgesicMixinPlugin, tk.DefaultDatasetForm):
    '''Implements IDatasetForm CKAN plugin to add some extra fields.

    Uses a tag vocabulary to add a custom metadata field to datasets.

    '''
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITranslation)

    # These record how many times methods that this plugin's methods are
    # called, for testing purposes.
    num_times_new_template_called = 0
    num_times_read_template_called = 0
    num_times_edit_template_called = 0
    num_times_comments_template_called = 0
    num_times_search_template_called = 0
    num_times_history_template_called = 0
    num_times_package_form_called = 0
    num_times_check_data_dict_called = 0
    num_times_setup_template_variables_called = 0

    # IConfigurer
    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_public_directory(config, 'public')
        tk.add_template_directory(config, 'templates')
        tk.add_resource('fanstatic', 'agesic')
        tk.add_ckan_admin_tab(config, 'agesic_admin_blueprint.ckanext_agesic_configuration', 'AGESIC Config')
        self.licenses_group_url = config['licenses_group_url']

        config['ckan.datasets_per_page'] = 5
        config['search.facets.default'] = 5

    def update_config_schema(self, schema):
        return schema

    # IAuth
    def get_auth_functions(self):
        return {'resource_show': datastore_search}

    def after_create(self, context, pkg_dict):
        # TODO: send mail
        log.debug("Created package %s" % str(pkg_dict))
        try:
            user = model.User.get(pkg_dict.get('creator_user_id'))
            group = model.Group.get(pkg_dict.get('owner_org'))
            extra_vars = {
                'site_url': config.get('ckan.site_url', ''),
                'name': pkg_dict.get('name'),
                'title': pkg_dict.get('title'),
                'group_name': group.name,
                'group_title': group.title,
                'creator_user_name': user.name,
            }
            SendNotificationController().send_package_create_notification(extra_vars)
            log.debug("Sent package create notification")
        except Exception as e:
            log.exception(e)

    def after_update(self, context, pkg_dict):
        # TODO: send mail
        log.info("Updated package %s" % str(pkg_dict))
        try:
            group = model.Group.get(pkg_dict.get('owner_org'))
            extra_vars = {
                'site_url': config.get('ckan.site_url', ''),
                'name': pkg_dict.get('name'),
                'title': pkg_dict.get('title'),
                'group_name': group.name,
                'group_title': group.title,
            }
            SendNotificationController().send_package_update_notification(extra_vars)
            log.debug("Sent package create notification")
        except Exception as e:
            log.exception(e)

    @staticmethod
    def __most_viewed():
        # TODO: change to join query package_stats and package
        connection = Session.connection()
        package_stat = dbutil.get_table('package_stats')
        s = select([
            package_stat.c.package_id, package_stat.c.visits_ever]). \
            where(package_stat.c.visits_ever > 5). \
            order_by(package_stat.c.visits_ever.desc()). \
            limit(350)
        return connection.execute(s).fetchall(), []

    def most_viewed_table(self):
        """
        Renders 7 most viewed datasets filter by user's organization or all if
        the user is admin.
        """
        packages = []
        user_groups = c.userobj.get_group_ids()
        if user_groups:
            package_stat = dbutil.get_table('package_stats')
            packs = Session.query(Package, package_stat.c.visits_ever). \
                filter(package_stat.c.package_id == Package.id). \
                filter(Package.private == False). \
                filter(Package.owner_org.in_(user_groups)). \
                filter(Package.state == 'active'). \
                order_by(package_stat.c.visits_ever.desc()).all()
            for package in packs:
                if package:
                    package_dict = package[0].as_dict()
                    package_dict['visits_ever'] = package[1]
                    packages.append(package_dict)
                    if len(packages) == 3:
                        break
        return tk.render_snippet(
            'home/most_viewed_table.html',
            {'packages': packages, 'truncate': 40})

    def most_viewed_hour(self):
        """
        Renders a chart for hours visits filtered by user's organization or all
        if the user is admin.
        """
        series = {}
        for p_id, days in json.loads(open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'public/tmp/ga_hour.json'), 'r').read()).items():
            p = Session.query(Package). \
                filter(Package.id == p_id). \
                filter(Package.private == False). \
                filter(Package.state == 'active').first()
            if authz.is_sysadmin(c.user) or (p and c.userobj.is_in_group(p.owner_org)):
                for day, visits in days.items():
                    for hour, vcount in visits.items():
                        val = series.get((day, hour), 0) + vcount
                        series[(day, hour)] = val
        result = [
            {'day': day, 'hour': hour, 'value': val} for (day, hour), val in
            series.items()]
        return tk.render_snippet(
            'home/most_viewed_hour.html', {'series': json.dumps(result)})

    def package_stats(self):
        """
        Package stats: dataset, recent visits, ever visits.
        Return HTML that can be rendered in the templates calling
        {{ h.package_stats() }}
        """
        packages = []
        allowed = False
        if (authz.is_sysadmin(c.user)):
            connection = Session.connection()
            package_stat = dbutil.get_table('package_stats')
            s = select([package_stat.c.package_id,
                        package_stat.c.visits_recently,
                        package_stat.c.visits_ever])
            res = connection.execute(s).fetchall()
            if res is not None and len(res) > 0:
                for package_id, recent, ever in res:
                    p = Session.query(Package).filter(
                        Package.id == package_id,
                        Package.type == 'dataset').first()
                    if p is not None:
                        name_url = p.name
                        name = p.title
                        pkt_url = '/dataset/{0}/'.format(name_url)
                        org_id = p.owner_org
                        r = Session.query(Group).filter(
                            Group.id == org_id).first()
                        if r is not None:
                            org = r.title
                        else:
                            org = ''
                        packages.append((name, pkt_url, org, recent, ever))
            allowed = True
        else:
            u = Session.query(User).filter(User.name == c.user).first()
            if u is not None:
                u_id = u.id
                orgs = Session.query(Member).filter(
                    Member.table_name == 'user',
                    Member.table_id == u_id,
                    Member.state == 'active',
                    Member.capacity == 'admin').all()
                if orgs is not None and len(orgs) > 0:
                    for o in orgs:
                        group_name = o.group.name
                        o_id = Session.query(Group).filter(
                            Group.name == group_name).first().id
                        res = Session.query(Package).filter(
                            Package.owner_org == o_id).all()
                        if res is not None and len(res) > 0:
                            for r in res:
                                if r.type == 'dataset':
                                    url_name = r.name
                                    name = r.title
                                    pkt_url = '/dataset/{0}/'.format(url_name)
                                    org = o.group.title
                                    connection = \
                                        Session.connection()
                                    package_stat = dbutil.get_table(
                                        'package_stats')
                                    s = select([package_stat.c.package_id,
                                                package_stat.c.visits_recently,
                                                package_stat.c.visits_ever]).\
                                                where(package_stat.c.package_id == r.id)
                                    res_1 = connection.execute(s).fetchall()
                                    if res_1 is not None and len(res_1) > 0:
                                        for package_id, recent, ever in res_1:
                                            packages.append((name,
                                                            pkt_url, org,
                                                            recent, ever))
                    allowed = True
        packages.sort(key=operator.itemgetter(2, 3, 4), reverse=True)
        data = {'top_packages': packages, 'allowed': allowed}
        return tk.render_snippet('snippets/package_stats_summary.html', data)

    def resource_stats(self):
        resources = []
        allowed = False
        if (authz.is_sysadmin(c.user)):
            connection = Session.connection()
            resource_stat = dbutil.get_table('resource_stats')
            s = select([resource_stat.c.resource_id,
                        resource_stat.c.visits_recently,
                        resource_stat.c.visits_ever])
            res = connection.execute(s).fetchall()
            if res is not None and len(res) > 0:
                for resource_id, recent, ever in res:
                    r = Session.query(Resource).filter(
                        Resource.id == resource_id).first()
                    if r is not None:
                        resource_url = '/dataset/{0}/resource/{1}'.format(
                            r.package_id, r.id)
                        if r.description is None or len(r.description) == 0:
                            descOrformat = r.format
                        else:
                            descOrformat = r.description
                        dataset = Session.query(Package).filter(
                            Package.id == r.package_id).first()
                        owner_org_id = dataset.owner_org
                        owner_org = Session.query(Group).filter(
                            Group.id == owner_org_id).first()
                        if owner_org is not None:
                            org = owner_org.title
                        else:
                            org = ''
                        dataset_name = dataset.title
                        datasetUrl = '/dataset/{0}/'.format(dataset.name)
                        resources.append((resource_url, descOrformat,
                                         datasetUrl, dataset_name,
                                         recent, ever, org))
            allowed = True
        else:
            u = Session.query(User).filter(User.name == c.user).first()
            if u is not None:
                u_id = u.id
                orgs = Session.query(Member).filter(
                    Member.table_name == 'user',
                    Member.table_id == u_id,
                    Member.state == 'active',
                    Member.capacity == 'admin').all()
                if orgs is not None and len(orgs) > 0:
                    connection = Session.connection()
                    resource_stat = dbutil.get_table('resource_stats')
                    s = select([resource_stat.c.resource_id,
                                resource_stat.c.visits_recently,
                                resource_stat.c.visits_ever])
                    res = connection.execute(s).fetchall()
                    if res is not None and len(res) > 0:
                        for o in orgs:
                            for r in res:
                                curr_res = Session.query(Resource).filter(
                                    Resource.id == r.resource_id).first()
                                if curr_res is not None:
                                    curr_pack_id = curr_res.package_id
                                    curr_pack = Session.query(Package).filter(
                                        Package.id == curr_pack_id).first()
                                    org_id = curr_pack.owner_org
                                    if org_id == o.group.id:
                                        resource_url = \
                                            '/dataset/{0}/resource/{1}'.format(
                                                curr_pack_id, r.resource_id)
                                        if (curr_res.description is None) or \
                                                len(curr_res.description) == 0:
                                            descOrformat = curr_res.format
                                        else:
                                            descOrformat = curr_res.description
                                        datasetUrl = '/dataset/{0}/'.format(
                                            curr_pack.name)
                                        dataset_name = curr_pack.title
                                        org = o.group.title
                                        recent = r.visits_recently
                                        ever = r.visits_ever
                                        resources.append((resource_url,
                                                          descOrformat,
                                                          datasetUrl,
                                                          dataset_name,
                                                          recent,
                                                          ever,
                                                          org))
                    allowed = True
        resources.sort(key=operator.itemgetter(6, 4, 5), reverse=True)
        data = {'top_resources': resources, 'allowed': allowed}
        return tk.render_snippet('snippets/resource_stats_summary.html', data)

    def __render_home_package_list(self, packages):
        data = {
            'packages': packages, 'list_class': "unstyled dataset-list", 'item_class': "dataset-item module-content",
            'truncate': 180, 'truncate_title': 70, 'hide_resources': True, 'show_package_organization': True}
        return tk.render_snippet('home/package_list.html', data)

    def most_viewed(self):
        """
        Most viewed 4 non private datasets.
        Return HTML that can be rendered in the templates calling
        {{ h.most_viewed() }}
        """
        packs, packages = self.__most_viewed()
        if packs:
            for p in packs:
                package = Session.query(Package). \
                    filter(Package.id == p.package_id). \
                    filter(Package.private == False). \
                    filter(Package.state == 'active'). \
                    first()
                if package:
                    package_dict = package.as_dict()
                    for g in package_dict['groups']:
                        group = Session.query(Group).filter(
                            Group.name == g).first()
                        if group.is_organization:
                            package_dict['organization'] = group.as_dict()
                            break
                    packages.append(package_dict)
                    if len(packages) == 4:
                        break
        return self.__render_home_package_list(packages)

    def most_recent(self):
        """
        Most recent datasets, based on the metadata_modified attr.
        Return HTML that can be rendered in the templates calling
        {{ h.most_recent() }}
        """
        packages = []
        result = Session.query(Package). \
            filter(Package.state == 'active'). \
            filter(Package.private == False). \
            filter(Package.type == 'dataset'). \
            order_by(Package.metadata_modified.desc()). \
            limit(4)
        for package in result:
            package_dict = package.as_dict()
            for g in package_dict['groups']:
                group = Session.query(Group).filter(Group.name == g).first()
                if group.is_organization:
                    package_dict['organization'] = group.as_dict()
                    break
            packages.append(package_dict)
        return self.__render_home_package_list(packages)

    def recent(self):
        """
        Recent datasets, based on the metadata_created attr.
        Return HTML that can be rendered in the templates calling
        {{ h.most_recent() }}
        """
        packages = []
        result = Session.query(Package). \
            filter(Package.private == False). \
            filter(Package.state == 'active'). \
            filter(Package.type == 'dataset'). \
            order_by(Package.metadata_created.desc()). \
            limit(4)
        for package in result:
            package_dict = package.as_dict()
            for g in package_dict['groups']:
                group = Session.query(Group).filter(Group.name == g).first()
                if group.is_organization:
                    package_dict['organization'] = group.as_dict()
                    break
            packages.append(package_dict)
        return self.__render_home_package_list(packages)

    def my_next_resources_due_dates(self):
        """
        Returns dates as keys of a dict with due resource elements inside.
        """
        resources_due_dates = []
        for dataset in tk.get_action('user_show')(
                None,
                {'id': c.userobj.id, 'include_datasets': True})['datasets']:
            dataset = Session.query(Package).filter(Package.id == dataset['id']).first()
            if not dataset:
                continue
            for res in dataset.resources:
                upd_freq = res.extras.get('update_frequency')
                if upd_freq and int(upd_freq) > 0:
                    res_modified_date = res.last_modified.date() if \
                        res.last_modified else res.created.date()
                    due_date = res_modified_date + timedelta(int(upd_freq))
                    if due_date < date.today():
                        resources_due_dates.append({
                            'due_date': due_date, 'resource': res,
                            'color': 'rojo'})
                    elif due_date < date.today() + timedelta(15):
                        resources_due_dates.append({
                            'due_date': due_date, 'resource': res,
                            'color': 'amarillo'})
                    else:
                        resources_due_dates.append({
                            'due_date': due_date, 'resource': res,
                            'color': 'verde'})
        resources_due_dates.sort(key=operator.itemgetter('due_date'))
        return tk.render_snippet(
            'home/resource_due_dates_list.html',
            {'resources_due_dates': resources_due_dates[:3]})

    def my_resources_broken_links(self):
        """
        Returns the first 3 broken link resources in my datasets
        """
        resources = []
        for dataset in tk.get_action('user_show')(
                None,
                {'id': c.userobj.id, 'include_datasets': True})['datasets']:
            dataset = Session.query(Package).filter(Package.id == dataset['id']).first()
            if not dataset:
                continue
            for res in dataset.resources:
                if link_health(get_resource_url(res, config, True), config):
                    resources.append(res)
                if len(resources) == 5:
                    break
            else:
                continue
            break
        return tk.render_snippet(
            'home/resource_broken_link_list.html', {'resources': resources})

    def most_popular_groups(self):
        """
        Top 9 groups
        """
        groups = tk.get_action('group_list')(
            data_dict={'sort': 'package_count desc', 'all_fields': True})
        groups = groups[:9]
        return groups

    def my_activity(self):
        """
        Returns the first 3 broken link resources in my datasets
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': c.userobj.id, 'user_obj': c.userobj, 'offset': 0}
        c.is_sysadmin = False
        user_dict = get_action('user_show')(context, data_dict)
        c.is_myself = user_dict['name'] == c.user
        filter_type = u''
        filter_id = u''
        c.dashboard_activity_stream = h.dashboard_activity_stream(c.userobj.id, filter_type, filter_id, 0)[:3]
        return tk.render_snippet('home/my_activities.html', {'activities': c.dashboard_activity_stream})

    def group_packages_count(self, group_id):
        group = Session.query(Group).filter(Group.id == group_id).first()
        return len(group.packages())

    def packages_count(self):
        return Session.query(Package).filter(
            Package.private == False,
            Package.state == 'active', Package.type == 'dataset').count()

    def organization_count(self):
        return Session.query(Group).filter(
            Group.state == 'active', Group.type == 'organization').count()

    def group_count(self):
        return Session.query(Group).filter(
            Group.state == 'active', Group.type == 'group').count()

    def most_popular_applications(self):
        """
        Most viewed showcase.
        Return HTML that can be rendered in the templates calling
        {{ h.most_popular_applications() }}
        """
        showcases = []
        connection = Session.connection()
        package_stat = dbutil.get_table('package_stats')
        s = select([package_stat.c.package_id,
                    package_stat.c.visits_recently,
                    package_stat.c.visits_ever]).order_by(
                        package_stat.c.visits_recently.desc())
        res = connection.execute(s).fetchall()
        if res is not None and len(res) > 0:
            for r in res:
                showcase = Session.query(Package).filter(
                    Package.id == r.package_id,
                    Package.type == 'showcase').first()
                if showcase:
                    showcases.append(showcase.as_dict())
                    if len(showcases) == 6:
                        break
        return showcases

    def revision_timestamp(self, resource):
        """
        Returns the revision timestamp of a resouce in string format.
        """
        rt = None
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
        # TODO: is necessary search activity?
        # act = Session.query(Activity).get(resource['revision_id'])
        for key in ('last_modified', 'metadata_modified', 'created'):
            if resource[key]:
                return datetime.strptime(resource[key], fmt)
        return rt

    def package_group_form(self):
        """
        Renders the form to add a Group to a package, only if the user who is
        editing is admin or package's org admin
        """
        if authz.is_sysadmin(c.user):
            group_dropdown = c.group_dropdown
        else:
            user = Session.query(User).filter(User.name == c.user).first()
            if hasattr(user, 'id') and c.pkg_dict['organization']['name'] in [
                o.group.name for o in Session.query(Member).filter(
                    Member.table_name == 'user',
                    Member.table_id == user.id,
                    Member.state == 'active',
                    Member.capacity.in_(['admin', 'editor'])).all()]:
                group_dropdown = [
                    (g.id, g.display_name) for g in Session.query(
                        Group).filter(Group.is_organization == False).all()]
                # Add this user to all groups via API using a sysadmin user
                # bypassing those is already member
                apikey = Session.query(User).filter(
                    User.name == 'default').first().apikey
                site_url = config.get('ckan.internal_site_url', config.get('ckan.site_url'))
                am_member = [g['id'] for g in tk.get_action(
                    'group_list_authz')(data_dict={'am_member': True})]
                for group_id, name in group_dropdown:
                    if group_id not in am_member:
                        # TODO: use verify setting
                        requests.post(
                            site_url + '/api/3/action/group_member_create',
                            headers={"Authorization": apikey}, json={
                                'id': group_id, 'username': user.id,
                                'role': 'member'}, verify=False)
            else:
                group_dropdown = []
        return tk.render_snippet(
            'package/snippets/group_form.html', {
                'group_dropdown': group_dropdown})

    def show_resource_state(self):
        state, dated = _('{state}'.format(state=c.resource['state'])), None
        if 'update_frequency' in c.resource:
            res_modified = self.revision_timestamp(c.resource)
            modified_ago = (datetime.today() - res_modified).days
            outdated, discontinued = timestatus(
                modified_ago, c.resource['update_frequency'])
            if discontinued:
                dated = 'discontinued'
            elif outdated:
                dated = 'outdated'
            if dated:
                return ', '.join([state, _('{dated}').format(dated=dated)])
        return state

    def iduruguay_link_manager(self):
        base_url = config.get('iduruguay.base_url', None)
        if (base_url and base_url == 'https://auth-testing.iduruguay.gub.uy/oidc/v1'):
            return "https://mi-testing.iduruguay.gub.uy"
        return "https://mi.iduruguay.gub.uy"

    def show_qa_stats(self):
        """
        Configuration variable
        """
        return config.get('agesic.show_qa_stats') == 'true'

    def show_archiver_stats(self):
        """
        Configuration variable
        """
        return config.get('agesic.show_archiver_stats') == 'true'

    def check_access_in_group(self, group_name):
        """
        Returns True iff the user logged in is admin or belongs to the group
        given by group_name
        """
        if c.userobj is None:
            return False
        if authz.is_sysadmin(c.user):
            result = True
        else:
            org = Session.query(Group).filter(Group.name == group_name).first()
            result = c.userobj.is_in_group(org.id)
        return result

    def get_update_frequency_text(self, value):
        return UPDATE_FREQS.get(str(value), u'Autogenerado')

    def get_update_frequency_text_resource(self, value):
        return UPDATE_FREQS.get(str(value), _('Not defined'))

    def package_update_frequency(self, resources):
        """
        Returns the min resources update_freq
        """
        try:
            freqs = [
                int(r['update_frequency']) for r in resources
                if r.get('update_frequency')]
        except Exception:
            freqs = False
        return UPDATE_FREQS[str(min(freqs))] if freqs else _('Not defined')

    def talk_comments(self):
        talk_root_url = config.get('agesic.talk_root_url', False)
        if talk_root_url:
            encoded_jwt, jwt_secret = None, config.get('agesic.talk_secret')
            userobj_id = None
            jwt_data = {
                'jti': uuid4().hex,
                "iat": int(time.time()),
                'exp': int(time.time()) + 3600
            }
            encoded_jwt = jwt.encode(jwt_data, jwt_secret)
            return tk.render_snippet('agesic/coral_talk_stream.html', {
                'talk_root_url': talk_root_url,
                'talk_auth_token': encoded_jwt,
                'userobj_id': userobj_id
            })
        return ''

    def get_helpers(self):
        return {
            'most_viewed': self.most_viewed,
            'most_viewed_table': self.most_viewed_table,
            'most_viewed_hour': self.most_viewed_hour,
            'most_recent': self.most_recent,
            'recent': self.recent,
            'package_stats': self.package_stats,
            'package_update_frequency': self.package_update_frequency,
            'get_update_frequency_text': self.get_update_frequency_text,
            'get_update_frequency_text_resource': self.get_update_frequency_text_resource,
            'resource_stats': self.resource_stats,
            'most_popular_groups': self.most_popular_groups,
            'most_popular_applications': self.most_popular_applications,
            'revision_timestamp': self.revision_timestamp,
            'package_group_form': self.package_group_form,
            'show_qa_stats': self.show_qa_stats,
            'show_resource_state': self.show_resource_state,
            'iduruguay_link_manager': self.iduruguay_link_manager,
            'show_archiver_stats': self.show_archiver_stats,
            'check_access_in_group': self.check_access_in_group,
            'group_packages_count': self.group_packages_count,
            'packages_count': self.packages_count,
            'organization_count': self.organization_count,
            'group_count': self.group_count,
            'my_next_resources_due_dates': self.my_next_resources_due_dates,
            'my_resources_broken_links': self.my_resources_broken_links,
            'my_activity': self.my_activity,
            'talk_comments': self.talk_comments
        }

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _modify_create_package_schema(self, schema):
        # Update default package schema
        schema.update({
            'title': [not_empty, unicode_safe],
            'private': [ignore_missing, private_if_not_sysadmin, boolean_validator],
            'author': [not_empty, unicode_safe],
            'author_email': [not_empty, unicode_safe, email_validator],
            'maintainer': [not_empty, unicode_safe],
            'maintainer_email': [not_empty, unicode_safe, email_validator],
            'license_id': [not_empty, unicode_safe],
            'notes': [not_empty, unicode_safe],
            'version': [not_empty, unicode_safe, package_version_validator],
            'update_frequency': [ignore_missing, update_frequency_validator, tk.get_converter('convert_to_extras')],
        })

        # Add our custom_resource fields to the schema
        schema['resources'].update({
            'name': [not_empty, unicode_safe],
            'description': [not_empty, unicode_safe],
            'format': [not_empty, clean_format, unicode_safe],
            'update_frequency': [update_frequency_validator],
            'spatial_ref_system': [ignore_missing],
            'spatial_coverage': [ignore_missing],
            'temporal_coverage': [ignore_missing]})
        return schema

    def _modify_update_package_schema(self, schema):
        # Update default package schema
        schema.update({
            'title': [ignore_missing, not_empty, unicode_safe],
            'private': [ignore_missing, private_if_not_sysadmin, boolean_validator],
            'author': [ignore_missing, not_empty, unicode_safe],
            'author_email': [ignore_missing, not_empty, unicode_safe, email_validator],
            'maintainer': [ignore_missing, not_empty, unicode_safe],
            'maintainer_email': [ignore_missing, not_empty, unicode_safe, email_validator],
            'license_id': [ignore_missing, not_empty, unicode_safe],
            'notes': [ignore_missing, not_empty, unicode_safe],
            'version': [ignore_missing, not_empty, unicode_safe, package_version_validator],
            'update_frequency': [ignore_missing, update_frequency_validator, tk.get_converter('convert_to_extras')],
        })
        # Add our custom_resource fields to the schema
        schema['resources'].update({
            'name': [ignore_missing, not_empty, unicode_safe],
            'description': [ignore_missing, not_empty, unicode_safe],
            'format': [ignore_missing, clean_format, unicode_safe],
            'update_frequency': [ignore_missing, update_frequency_validator],
            'spatial_ref_system': [ignore_missing],
            'spatial_coverage': [ignore_missing],
            'temporal_coverage': [ignore_missing]})
        return schema

    def create_package_schema(self):
        schema = super(AgesicIDatasetFormPlugin, self).create_package_schema()
        schema = self._modify_create_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(AgesicIDatasetFormPlugin, self).update_package_schema()
        schema = self._modify_update_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(AgesicIDatasetFormPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(tk.get_converter('free_tags_only'))

        # Add our custom country_code metadata field to the schema.
        schema.update({
            'update_frequency': [
                tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
        })

        # Add our custom_resource fields to the schema
        schema['resources'].update({
            'update_frequency': [tk.get_validator('ignore_missing')],
            'spatial_ref_system': [tk.get_validator('ignore_missing')],
            'spatial_coverage': [tk.get_validator('ignore_missing')],
            'temporal_coverage': [tk.get_validator('ignore_missing')]})

        return schema

    # These methods just record how many times they're called, for testing
    # purposes.
    # TODO: It might be better to test that custom templates returned by
    # these methods are actually used, not just that the methods get
    # called.

    def setup_template_variables(self, context, data_dict):
        AgesicIDatasetFormPlugin.num_times_setup_template_variables_called += 1
        return super(
            AgesicIDatasetFormPlugin, self).setup_template_variables(context, data_dict)

    def new_template(self):
        AgesicIDatasetFormPlugin.num_times_new_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).new_template()

    def read_template(self):
        AgesicIDatasetFormPlugin.num_times_read_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).read_template()

    def edit_template(self):
        AgesicIDatasetFormPlugin.num_times_edit_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).edit_template()

    def comments_template(self):
        AgesicIDatasetFormPlugin.num_times_comments_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).comments_template()

    def search_template(self):
        AgesicIDatasetFormPlugin.num_times_search_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).search_template()

    def history_template(self):
        AgesicIDatasetFormPlugin.num_times_history_template_called += 1
        return super(AgesicIDatasetFormPlugin, self).history_template()

    def package_form(self):
        AgesicIDatasetFormPlugin.num_times_package_form_called += 1
        return super(AgesicIDatasetFormPlugin, self).package_form()

    # check_data_dict() is deprecated, this method is only here to test that
    # legacy support for the deprecated method works.
    def check_data_dict(self, data_dict, schema=None):
        AgesicIDatasetFormPlugin.num_times_check_data_dict_called += 1

    # IPackageController

    def _add_to_pkg_dict(self, context, pkg_dict):
        '''
        Add key/values to pkg_dict and return it.
        '''

        if pkg_dict['type'] != 'showcase':
            license_id = pkg_dict.get('license_id')
            if license_id:
                for license in json.loads(
                        urllib.request.urlopen(self.licenses_group_url).read()):
                    if license.get('id') == license_id:
                        pkg_dict[u'license_url'] = license.get('url')
                        break

        return pkg_dict

    def after_show(self, context, pkg_dict):
        '''
        Modify package_show pkg_dict.
        '''
        pkg_dict = self._add_to_pkg_dict(context, pkg_dict)

    def before_view(self, pkg_dict):
        '''
        Modify pkg_dict that is sent to templates.
        '''

        context = {'model': model, 'session': Session,
                   'user': tk.c.user or tk.c.author}

        return self._add_to_pkg_dict(context, pkg_dict)

    # Translations (taken from ckanext-showcase plugin)

    def i18n_directory(self):
        '''Change the directory of the *.mo translation files

        The default implementation assumes the plugin is
        ckanext/myplugin/plugin.py and the translations are stored in
        i18n/
        '''
        # assume plugin is called ckanext.<myplugin>.<...>.PluginClass
        extension_module_name = '.'.join(self.__module__.split('.')[0:2])
        module = sys.modules[extension_module_name]
        return os.path.join(os.path.dirname(module.__file__), 'i18n')

    def i18n_locales(self):
        '''Change the list of locales that this plugin handles

        By default the will assume any directory in subdirectory in the
        directory defined by self.directory() is a locale handled by this
        plugin
        '''
        directory = self.i18n_directory()
        return [d for
                d in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, d))]

    def i18n_domain(self):
        '''Change the gettext domain handled by this plugin

        This implementation assumes the gettext domain is
        ckanext-{extension name}, hence your pot, po and mo files should be
        named ckanext-{extension name}.mo'''
        return 'ckanext-{name}'.format(name=self.name)

    # IFacets

    def __get_default_facet(self):
        return 'groups tags organization res_format license_id'.split()

    def __get_default_facet_titles(self):
        return {
            'tags': _('Tags'),
            'organization': _('Organizations'),
            'groups': _('Groups'),
            'res_format': _('Formats'),
            'license_id': _('Licenses'),
        }

    def dataset_facets(self, facets_dict, package_type):
        return self.get_facets_dict(facets_dict, self.__get_default_facet(), self.__get_default_facet_titles())

    def group_facets(self, facets_dict, group_type, package_type):
        return self.get_facets_dict(facets_dict, self.__get_default_facet(), self.__get_default_facet_titles())

    def organization_facets(self, facets_dict, organization_type, package_type):
        default_facet_titles = {
            'tags': _('Tags'),
            'groups': _('Groups')
        }
        return self.get_facets_dict(facets_dict, self.__get_default_facet(), default_facet_titles)

    def get_facets_dict(self, facets_dict, default_facet, default_facet_titles):
        return facets_dict
