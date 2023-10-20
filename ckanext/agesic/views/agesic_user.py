import logging

import time
import jwt
import io
import os
import json
import pycountry

from uuid import uuid4
from datetime import datetime
from redminelib import Redmine
import csv

from flask import Blueprint, make_response
from ckan.model import Session, Package
from ckan.common import config, g, _

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.logic as logic
import ckan.authz as authz

abort = base.abort
render = base.render
from flask import request

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

log = logging.getLogger(__name__)


def __user_setup_template_variables(id=None, context=None, data_dict=None):
    if context is None:
        context = {'model': model, 'session': model.Session,
                   'user': g.user, 'auth_user_obj': g.userobj,
                   'for_view': True}
    if data_dict is None:
        data_dict = {'id': id,
                     'user_obj': g.userobj,
                     'include_num_followers': True}
    is_sysadmin = authz.is_sysadmin(g.user)
    try:
        user_dict = logic.get_action(u'user_show')(context, data_dict)
    except logic.NotFound:
        abort(404, _(u'User not found'))
    except logic.NotAuthorized:
        abort(403, _(u'Not authorized to see this page'))

    is_myself = user_dict[u'name'] == g.user
    about_formatted = h.render_markdown(user_dict[u'about'])
    extra = {
        u'include_datasets': True,
        u'capacity': 'member',
        u'include_dataset_count': False,
        u'include_num_followers': True,
        u'is_sysadmin': is_sysadmin,
        u'user_dict': user_dict,
        u'is_myself': is_myself,
        u'about_formatted': about_formatted
    }

    g.is_sysadmin = is_sysadmin
    g.user_dict = user_dict
    g.is_myself = is_myself
    g.about_formatted = about_formatted
    return extra


def agesic_user_organizations(id=None):
    __user_setup_template_variables(id=id)
    try:
        organizations = get_action(u'organization_list_for_user')({u'user': id}, {u'capacity': u'member'})
    except ValidationError:
        abort(400)
    return render('user/user_organizations.html', extra_vars={
        'user_dict': g.user_dict,
        'organizations': organizations})


def agesic_user_groups(id=None):
    __user_setup_template_variables(id=id)
    try:
        groups = get_action('group_list_authz')({u'user': id}, data_dict={'am_member': True})
    except ValidationError:
        abort(400)
    return base.render('user/user_groups.html', extra_vars={
        'user_dict': g.user_dict,
        'groups': groups})


def __get_jwt_token():
    # JWT TOKEN
    return TOKEN


def __publicador_render(url, dst):
    encoded_jwt = __get_jwt_token()
    iframe_url = '{}?token={}'.format(url, encoded_jwt, dst)
    log.info("Render iframe %s" % iframe_url)
    return base.render('agesic/publicador_da.html', extra_vars={'iframe_url': iframe_url})


def publicador_da():
    """
    Renders a page containing an iframe loaded from a third party service
    authorized with a JWT given by query parameter
    """
    url = config.get('agesic.publicador_da_url', '$PENTAHO_PUBLICADOR_1')
    if url == '$PENTAHO_PUBLICADOR_1':
        # TODO: Harcoded by compatibility with deploy, remove in future
        url = URL
    return __publicador_render(url, 'formApertura')


def publicador_da_2():
    """
    Renders a page containing an iframe loaded from a third party service
    authorized with a JWT given by query parameter
    """
    url = config.get('agesic.publicador_da_url_2', '$PENTAHO_PUBLICADOR_2')
    if url == '$PENTAHO_PUBLICADOR_2':
        # TODO: Harcoded by compatibility with deploy, remove in future
        url = URL
    return __publicador_render(url, 'formActualizar')


def redmine_issue_report():
    name = email = ""
    if request.method.upper() == 'POST':
        try:
            log.info("Sending request to redmine: %s" % str(request.form))
            name = request.form.get('name', '')
            email = request.form.get('email', '')
            comments = request.form.get('comments', False)
            url = config.get("agesic.issue_redmine.url", False)
            apikey = config.get("agesic.issue_redmine.apikey", False)
            project = config.get("agesic.issue_redmine.project", False)
            if url and email:
                to_date = datetime.now().strftime("%Y%m%d")
                redmine = Redmine(url, key=apikey, requests={'verify': False})
                issue = redmine.issue.create(
                    project_id=project,
                    subject=" - ".join([to_date, email, name]),
                    description=comments
                )
                log.info("Issue created: {}".format(issue.id))
                h.flash_success(_('Se ha recepcionado su solucitud, muchas gracias'))
        except Exception as e:
            h.flash_error(_('Ha ocurrido un error, por favor intentar más tarde'))
            abort('Something wrong: %s' % e)
    elif g.userobj:
        name = g.userobj.fullname
        email = g.userobj.email
    return base.render('agesic/redmine_issue_report.html', extra_vars={"name": name, "email": email})


def most_viewed_geo():
    """
    Renders a map for country visits filtered by user's organization or all
    if the user is admin.
    """
    series = {}
    for p_id, visits in json.loads(open(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../public/tmp/ga_geo.json'), 'r').read()).items():
        p = Session.query(Package).filter(Package.id == p_id).first()
        if authz.is_sysadmin(g.user) or g.userobj.is_in_group(p.owner_org):
            for iso2, vcount in visits.items():
                cc = pycountry.countries.get(alpha_2=iso2)
                if cc is not None:
                    iso3 = pycountry.countries.get(alpha_2=iso2).alpha_3
                    val = series.get(iso3, 0) + vcount
                    series[iso3] = val
    response = make_response()
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(('iso3', 'visitas'))
    writer.writerows(series.items())
    response.data = buffer.getvalue()
    return response


agesic_user_blueprint = Blueprint(u'agesic_user_blueprint', __name__, url_prefix='/agesic/user')
agesic_user_blueprint.add_url_rule(u'/agesic_user_organizations/<id>', 'agesic_user_organizations',
                                   view_func=agesic_user_organizations)
agesic_user_blueprint.add_url_rule(u'/issue_report', 'issue_report', methods=[u'GET', u'POST'],
                                   view_func=redmine_issue_report)
agesic_user_blueprint.add_url_rule(u'/agesic_user_groups/<id>', 'agesic_user_groups',
                                   view_func=agesic_user_groups)
agesic_user_blueprint.add_url_rule(u'/publicador_da', 'publicador_da', view_func=publicador_da)
agesic_user_blueprint.add_url_rule(u'/publicador_da_2', 'publicador_da_2', view_func=publicador_da_2)
agesic_user_blueprint.add_url_rule(u'/most_viewed_geo', 'most_viewed_geo', view_func=most_viewed_geo)


@agesic_user_blueprint.before_request
def before_request():
    try:
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj,
            u'for_view': True
        }
        data_dict = {
            u'user_obj': g.userobj,
            u'include_num_followers': True
        }
        logic.check_access(u'user_show', context, data_dict)
    except logic.NotFound:
        abort(404, _(u'User not found'))
    except logic.NotAuthorized:
        abort(403, _(u'Not authorized to see this page'))
