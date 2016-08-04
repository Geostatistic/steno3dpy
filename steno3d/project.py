"""project.py contains the project class that contains resources
in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from tratlets import Bool

from .base import CompositeResource, UserContent
from .client import Comms, get, needs_login
from .trait import KeywordInstance, Repeated, validator


QUOTA_REACHED = """
Uploading this {priv} project will put you over your quota
of {num} {priv} project(s). For more projects and space, consider
upgrading your account: https://steno3d.com/settings/plan
"""

QUOTA_IMPENDING = """
After this project, you may upload {remaining} more {priv} project(s) before
reaching your {priv} project quota. For more projects and space
consider upgrading your account: https://steno3d.com/settings/plan
"""


class Project(UserContent):
    """Steno3D top-level project"""
    _model_api_location = 'project/steno3d'

    resources = Repeated(
        help='Project Resources',
        trait=KeywordInstance(klass=CompositeResource)
    )

    public = Bool(
        help='Public visibility of project',
        default_value=False
    )

    _public_online = None

    @classmethod
    def _url_view_from_uid(cls, uid):
        """Get full url from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=Comms.base_url,
            mapi='app',
            uid=uid)
        return url

    def _nbytes(self):
        return sum(r._nbytes() for r in self.resources)

    @needs_login
    def upload(self, sync=False, verbose=True, print_url=True):
        """Upload the project"""
        if getattr(self, '_upload_data', None) is None:
            assert self.validate()

            self._check_project_quota(verbose)
            self._public_online = self.public
        elif verbose and self._public_online:
            print('This project is PUBLIC. It is viewable by everyone.')
        if verbose and not self._public_online == self.public:
            print('Local privacy changes cannot be applied to '
                  'projects that are already uploaded. To make '
                  'these changes, please use the dashboard on '
                  'steno3d.com.')
        self._upload(sync, verbose)
        self._trigger_ACL_fix()
        if print_url:
            print(self._url)
        return self._url

    def _trigger_ACL_fix(self):
        self._put({})

    @validator
    def validate(self):
        """Check if project resource pointers are correct"""
        for res in self.resources:
            if self not in res.project:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that resources point to containing '
                                 'project.')
        self._validate_project_size()
        return True

    def _validate_project_size(self):
        if Comms.user.logged_in:
            res_limit = Comms.user.project_resource_limit
            if len(self.resources) > res_limit:
                raise ValueError(
                    'Total number of resources in project ({res}) '
                    'exceeds limit: {lim}'.format(res=len(self.resources),
                                                  lim=res_limit)
                )
            size_limit = Comms.user.project_size_limit
            if self._nbytes() > size_limit:
                raise ValueError(
                    'Total project size ({file} bytes) exceeds limit: '
                    '{lim} bytes'.format(file=self._nbytes(),
                                         lim=size_limit)
                )
        return True

    def _on_property_change(self, name, pre, post):
        if name == 'resources':
            if pre is None:
                pre = []
            if post is None:
                post = []
            for res in post:
                if res not in pre and self not in res.project:
                    res.project += [self]
            for res in pre:
                if res not in post and self in res.project:
                    res.project = [p for p in res.project
                                   if p is not self]
            if len(set(post)) != len(post):
                post_post = []
                for r in post:
                    if r not in post_post:
                        post_post += [r]
                self.resources = post_post
        super()._on_property_change(name, pre, post)

    def _upload_dirty(self, sync=False, verbose=True, tab_level=''):
        dirty = self._dirty
        if 'resources' in dirty:
            [r._upload(sync, verbose, tab_level) for r in self.resources]

    def _get_dirty_data(self, force=False, initialize=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        if 'public' in dirty or force:
            datadict['public'] = self.public
        if ('resources' in dirty or force) and not initialize:
            datadict['resourceUids'] = ','.join(
                (r._json['longUid'] for r in self.resources)
            )
        return datadict

    def _check_project_quota(self, verbose=True):
        if self.public:
            privacy = 'public'
        else:
            privacy = 'private'
        if verbose:
            print('Verifying your quota for ' + privacy + ' projects...')
        resp = get('check/quota?test=ProjectSteno3D')
        resp = resp.json()[privacy]
        if resp['quota'] == 'Unlimited':
            pass
        elif resp['count'] >= resp['quota']:
            raise Exception(QUOTA_REACHED.format(
                                priv=privacy,
                                num=resp['quota']
                            ))
        elif verbose and (resp['quota'] - resp['count'] - 1) < 4:
            print(QUOTA_IMPENDING.format(
                    remaining=resp['quota'] - resp['count'] - 1,
                    priv=privacy
                  ))
        if verbose and self.public:
            print('This PUBLIC project will be viewable by everyone.')


    @property
    def _url(self):
        if getattr(self, '_upload_data', None) is not None:
            return self._url_view_from_uid(self._upload_data['uid'])

    @property
    @needs_login
    def url(self):
        """steno3d.com url of project if uploaded"""
        if getattr(self, '_upload_data', None) is None:
            print('Project not uploaded: Please upload() '
                  'before accessing the URL.')
        return self._url


__all__ = ['Project']
