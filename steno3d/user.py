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
    email = properties.String('email')
    name = properties.String('name')
    url = properties.String('url')
    affiliation = properties.String('affiliation')
    location = properties.String('location')
    username = properties.String('username')

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
        default=15
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._on_property_change = self._immutable_properties

    def _immutable_properties(self, prop, pre, post):
        if not pre == post:
            print('User data must be modified in settings at steno3d.com')
            setattr(self, '_p_' + prop, pre)
