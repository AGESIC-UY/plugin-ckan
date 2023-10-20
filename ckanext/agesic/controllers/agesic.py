import logging
import requests

from ckan.plugins import toolkit as tk
import ckan.model as model
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.model import ResourceView, Resource, Package, Session, User, Group
from ckan.common import config, json, response
from ckan.lib.base import BaseController
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.uploader as uploader

import paste.fileapp
import mimetypes

import jwt
import time
from uuid import uuid4

_ = tk._
c = tk.c
request = tk.request
render = tk.render
abort = tk.abort
redirect = tk.redirect_to
NotFound = tk.ObjectNotFound
ValidationError = tk.ValidationError
check_access = tk.check_access
get_action = tk.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
NotAuthorized = tk.NotAuthorized

log = logging.getLogger(__name__)


class AgesicCustomController(BaseController):

    def agesic_resource_view(self, id, resource_id, view_id=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user,
                   'auth_user_obj': c.userobj}
        if request.params.get('resource_view', ''):
            abort(409, _('Bad resource view data'))
        elif view_id:
            try:
                package = Package.get(id)
                package.private = False
                package_dict = model_dictize.package_dictize(package, context)
                resource = Resource.get(resource_id)
                resource_dict = model_dictize.resource_dictize(
                    resource, context)
                view = ResourceView.get(view_id)
                if view and resource and package:
                    context['resource_view'] = view
                    resource_tmp = Resource.get(view.resource_id)
                    context['resource'] = resource_tmp
                    view_dict = model_dictize.resource_view_dictize(
                        view, context)
                else:
                    abort(404, _('Resource view not found'))
            except (NotFound, NotAuthorized):
                abort(404, _('Resource view not found'))
        return h.rendered_resource_view(
            view_dict, resource_dict, package_dict, embed=True)

    def resource_download(self, id, resource_id, filename=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}
        try:
            # skip the verification permission for geojson
            if filename and not filename.endswith('.geojson'):
                rsc = get_action('resource_show')(context, {'id': resource_id})
                get_action('package_show')(context, {'id': id})
            else:
                resource = Resource.get(resource_id)
                assert resource
                rsc = model_dictize.resource_dictize(resource, context)
        except (NotFound, NotAuthorized, AssertionError):
            abort(404, _('Resource not found'))
        if rsc.get('url_type') == 'upload':
            upload = uploader.get_resource_uploader(rsc)
            filepath = upload.get_path(rsc['id'])
            fileapp = paste.fileapp.FileApp(filepath)
            try:
                status, headers, app_iter = request.call_application(fileapp)
            except OSError:
                abort(404, _('Resource data not found'))
            response.headers.update(dict(headers))
            content_type, content_enc = mimetypes.guess_type(
                rsc.get('url', ''))
            if content_type:
                response.headers['Content-Type'] = content_type
            response.status = status
            return app_iter
        elif 'url' not in rsc:
            abort(404, _('No download is available'))
        h.redirect_to(rsc['url'])
