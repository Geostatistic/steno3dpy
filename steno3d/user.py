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


    def _on_prop_change(self, prop, pre, post):
        if not pre == post:
            print('User data must be modified in settings at steno3d.com')
            setattr(self, '_p_' + prop, pre)


    def _login(self, login_json):
        setattr(self, '_p_username', login_json['uid'])
        setattr(self, '_p_email', login_json['email'])
        setattr(self, '_p_name', login_json['name'])
        setattr(self, '_p_url', login_json['url'])
        setattr(self, '_p_affiliation', login_json['affiliation'])
        setattr(self, '_p_location', login_json['location'])

    @property
    def logged_in(self):
        return True



    def get_user(self):
        if getattr(self, '_me', None) is not None:
            return self._me
        elif getattr(self, '_user', None) is None:
            return None
        else:
            username = self._user['uid']
            email = self._user['email']
            name = self._user['name']
            url = self._user['url']
            affiliation = self._user['affiliation']
            location = self._user['location']
            self._me = User(
                username=username if username is not None else 'None',
                email=email if email is not None else 'None',
                name=name if name is not None else 'None',
                url=url if url is not None else 'None',
                affiliation=affiliation if affiliation is not None else 'None',
                location=location if location is not None else 'None',
            )
            return self._me
