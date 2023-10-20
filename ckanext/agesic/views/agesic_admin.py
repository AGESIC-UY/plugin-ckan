import logging
import requests

from flask import Blueprint
from ckan.model import Session, Group, User, State

from sqlalchemy.sql.expression import or_

from ckan.common import config, g, _
from ckan.views.api import _finish_ok

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.logic as logic

abort = base.abort
render = base.render
request = base.request

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

log = logging.getLogger(__name__)


def user_autocomplete(q):
    limit = request.params.get('limit', 15)
    user_list = []
    if q:
        query = Session.query(User)
        query = query.filter(User.state != State.DELETED)
        qstr = '%' + q + '%'
        filters = [
            User.name.ilike(qstr),
            User.fullname.ilike(qstr),
            User.email.ilike(qstr),
        ]
        query = query.filter(or_(*filters))
        query = query.limit(limit)
        for user in query.all():
            result_dict = {}
            for k in ['name', 'email']:
                result_dict[k] = getattr(user, k)
            result_dict['info'] = getattr(user, 'name') + ' (' + getattr(user, 'email') + ')'
            user_list.append(result_dict)
    return _finish_ok(user_list)


def manage_agesic_configuration():
    talk_root_url = config.get('agesic.talk_root_url')
    if talk_root_url:
        talk_admin_url = talk_root_url + '/admin/moderate'
    else:
        talk_admin_url = None
    extra_vars = {
        'errors': {},
        'talk_admin_url': talk_admin_url}
    return base.render('admin/manage_agesic_configuration.html', extra_vars=extra_vars)



agesic_admin_blueprint = Blueprint(u'agesic_admin_blueprint', __name__, url_prefix='/ckan-admin')
agesic_admin_blueprint.add_url_rule(u'/agesic/utils/autocomplete/<q>', 'user_autocomplete', view_func=user_autocomplete)
agesic_admin_blueprint.add_url_rule(u'/agesic_configuration', 'ckanext_agesic_configuration',
                                    view_func=manage_agesic_configuration)


@agesic_admin_blueprint.before_request
def before_request():
    try:
        context = dict(model=model, user=g.user, auth_user_obj=g.userobj)
        logic.check_access(u'sysadmin', context)
    except NotAuthorized:
        abort(403, _(u'Need to be system administrator to administer'))
