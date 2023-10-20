import ckan.plugins as p
from ckan import model
from ckan.lib.base import BaseController

class AppsController(BaseController):

    def index(self):
        c = p.toolkit.c
        c.related = model.Session.query(model.Related).filter(
            model.Related.type=='application')
        return p.toolkit.render('apps/index.html')
