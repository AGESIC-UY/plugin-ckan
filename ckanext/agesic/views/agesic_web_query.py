import logging

from flask import Blueprint

from ckan.common import g, _

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

result = []


def __check_query(tmp_query):
    tmp_query = tmp_query.replace('\n', '').replace(';', '')
    tmp_query = tmp_query.strip()
    select = tmp_query.lower().count('select')
    update = tmp_query.lower().count('update')
    delete = tmp_query.lower().count('delete')
    if select + update + delete != 1:
        raise Exception('Invalid query')
    limit = tmp_query.lower().count('limit')
    if limit == 0 and select:
        tmp_query = tmp_query + ' limit 10'
    return tmp_query


def index():
    return base.render('web_query/index.html')


def query():
    try:
        if request.method != 'POST':
            raise Exception('Invalid method')

        data = request.form
        code = str(data.get('code'))
        q = __check_query(code)
        log.info("Executing query: %s" % q)
        engine = model.meta.engine
        result = 'NO DATA'
        arr1 = engine.execute(q)
        if q.lower().startswith('select') and arr1.rowcount > 0:
            result = str(arr1.fetchall())
        h.flash_success(_('Query executed with result: %s' % result))
        url = h.url_for('agesic_web_query_blueprint.index')
        return h.redirect_to(url)
    except Exception as e:
        msg = _('Failed to execute query: ' + str(e))
        h.flash_error(msg)
        return h.redirect_to(u'agesic_web_query_blueprint.index')


agesic_web_query_blueprint = Blueprint(u'agesic_web_query_blueprint', __name__, url_prefix='/web-query-admin')
agesic_web_query_blueprint.add_url_rule(u'/index', 'index', methods=[u'GET'], view_func=index)
agesic_web_query_blueprint.add_url_rule(u'/query', 'query', methods=[u'POST'], view_func=query)


@agesic_web_query_blueprint.before_request
def before_request():
    try:
        context = dict(model=model, user=g.user, auth_user_obj=g.userobj)
        logic.check_access(u'sysadmin', context)
        if g.userobj.name not in ['servinfo', 'uy-ci-61748091']:
            raise NotAuthorized()
    except NotAuthorized:
        abort(403, _(u'Need to be system administrator to administer'))
