"""user.py contains basic information about the steno3d user"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from traitlets import Int, Unicode

from .traits import DelayedValidator


class User(DelayedValidator ):
    """Class representing a user instance"""
    _model_api_location = "user"
    email = Unicode(
        help='Email',
        allow_none=True
    )
    name = Unicode(
        help='Name',
        allow_none=True
    )
    url = Unicode(
        help='URL',
        allow_none=True
    )
    affiliation = Unicode(
        help='Affiliation',
        allow_none=True
    )
    location = Unicode(
        help='Location',
        allow_none=True
    )
    username = Unicode(
        help='Username',
        default_value=None,
        allow_none=True
    )

    devel_key = Unicode(
        help='Developer API Key',
        allow_none=True
    )

    file_size_limit = Int(
        help='Inidividual file limit',
        default_value=5000000
    )
    project_size_limit = Int(
        help='Project size limit',
        default_value=25000000
    )
    project_resource_limit = Int(
        help='Maximum resources in a project',
        default_value=25
    )

    # def _on_prop_change(self, prop, pre, post):
    #     if not pre == post:
    #         print('User data must be modified in settings at steno3d.com')
    #         self.' + prop, pre)

    def login_with_json(self, login_json):
        self.username = login_json['uid']
        self.email = login_json['email']
        self.name = login_json['name']
        self.url = login_json['url']
        self.affiliation = login_json['affiliation']
        self.location = login_json['location']

    def set_key(self, devel_key):
        self.devel_key = devel_key

    def logout(self):
        self.username = None
        self.email = None
        self.name = None
        self.url = None
        self.affiliation = None
        self.location = None
        self.devel_key = None

    @property
    def logged_in(self):
        return self.username is not None
