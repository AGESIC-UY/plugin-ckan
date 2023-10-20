import logging

from flask import Blueprint, make_response
import json

from ckan.model import Session, User
from ckan.common import config, g, _

from ckan.views.api import _finish_ok
import ckan.lib.base as base
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


def __get_groups_for_user(user, group_type=None):
    q = Session.query(model.Group, model.Member.capacity) \
        .join(model.Member, model.Member.group_id == model.Group.id and \
              model.Member.table_name == 'user'). \
        join(model.User, model.User.id == model.Member.table_id). \
        filter(model.Member.state == 'active'). \
        filter(model.Member.table_id == user.id)
    result = q.all()
    groups = []
    if group_type:
        for g, capacity in result:
            g_as_dict = g.as_dict()
            if g.type == group_type:
                g_as_dict['rol'] = capacity
                groups.append(g_as_dict)
    return groups

def users(username=None):
    result = []
    user_set = Session.query(User).filter(User.name == username) if username else User.all()
    for u in user_set:
        u_as_dict = u.as_dict()
        u_as_dict['organizations'] = __get_groups_for_user(u, 'organization')
        u_as_dict['categories'] = __get_groups_for_user(u, 'group')
        result.append(u_as_dict)
    response = make_response()
    response.headers['Content-Type'] = 'application/json'
    response.data = json.dumps(result)
    return response


agesic_api_pentaho_blueprint = Blueprint(u'agesic_api_pentaho_blueprint', __name__, url_prefix='/agesic')
agesic_api_pentaho_blueprint.add_url_rule(u'/users', 'all_users', view_func=users)
agesic_api_pentaho_blueprint.add_url_rule(u'/users/<username>', 'users', view_func=users)


@agesic_api_pentaho_blueprint.before_request
def before_request():
    try:
        context = dict(model=model, user=g.user, auth_user_obj=g.userobj)
        logic.check_access(u'sysadmin', context)
    except NotAuthorized:
        users = config.get('agesic.users_api', []).split()
        if g.user not in users:
            abort(403, _('Not authorized'))
