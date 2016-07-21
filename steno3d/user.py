"""user.py contains basic information about the steno3d user"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

import properties


class User(properties.PropertyClass):
    """Class representing a user instance"""
    _model_api_location = "user"
    email = properties.String('Email')
    name = properties.String('Name')
    url = properties.String('URL')
    affiliation = properties.String('Affiliation')
    location = properties.String('Location')
    username = properties.String('Username')

    devel_key = properties.String('Developer API Key')

    file_size_limit = properties.Int(
        'Inidividual file limit',
        default=5000000
    )
    project_size_limit = properties.Int(
        'Project size limit',
        default=25000000
    )
    project_resource_limit = properties.Int(
        'Maximum resources in a project',
        default=25
    )

    def _on_prop_change(self, prop, pre, post):
        if not pre == post:
            print('User data must be modified in settings at steno3d.com')
            setattr(self, '_p_' + prop, pre)

    def login_with_json(self, login_json):
        setattr(self, '_p_username', login_json['uid'])
        setattr(self, '_p_email', login_json['email'])
        setattr(self, '_p_name', login_json['name'])
        setattr(self, '_p_url', login_json['url'])
        setattr(self, '_p_affiliation', login_json['affiliation'])
        setattr(self, '_p_location', login_json['location'])

    def set_key(self, devel_key):
        setattr(self, '_p_devel_key', devel_key)

    def logout(self):
        setattr(self, '_p_username', None)
        setattr(self, '_p_email', None)
        setattr(self, '_p_name', None)
        setattr(self, '_p_url', None)
        setattr(self, '_p_affiliation', None)
        setattr(self, '_p_location', None)
        setattr(self, '_p_devel_key', None)

    @property
    def logged_in(self):
        return self.username is not None
