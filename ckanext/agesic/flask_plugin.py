# -*- coding: utf-8 -*-
import ckan.plugins as plugins
from ckanext.agesic.cli import get_commands
from ckanext.agesic.blueprint import get_blueprints


class AgesicMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    # IBlueprint
    def get_blueprint(self):
        return get_blueprints()

    # IClick
    def get_commands(self):
        return get_commands()
