"""resource.py contains the base resource classes that user-created
resources depend on in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from json import dumps

import properties

from .client import Comms
from .client import needs_login
from .client import plot
from .content import UserContent


class BaseResource(UserContent):
    """Base class for all resources that are added to projects and
    uploaded to steno3d
    """
    meta = properties.Object('Meta data in JSON form.', default={})

    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty
        if 'opts' in dirty or (force and hasattr(self, 'opts')):
            datadict['meta'] = self.opts._json
            self.opts._mark_clean(recurse=False)
        return datadict

    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        return True


    def _validate_file_size(self, name):
        if Comms.get_user() is not None:
            file_limit = Comms.get_user().file_size_limit
            if self.nbytes(name) > file_limit:
                raise ValueError(
                    '{name} file size ({file} bytes) exceeds limit: '
                    '{lim} bytes'.format(name=name,
                                         file=self.nbytes(name),
                                         lim=file_limit)
                )
        return True


class CompositeResource(BaseResource):
    """A composite resource that stores references to lower-level
    objects, and may also grant access to them through ACL delegation.
    """
    project = properties.Pointer(
        'Project',
        ptype='Project',
        required=True,
        repeated=True
    )
    _children = {
        'mesh': None,
        'data': 'data',
        'textures': None,
    }

    def __init__(self, project=None, **kwargs):
        if project is None:
            raise TypeError('Resource must be constructed with its '
                            'containing project(s)')
        super().__init__(**kwargs)
        self.project = project

    @classmethod
    def _url_view_from_uid(cls, uid):
        """Get full url from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=Comms.base_url,
            mapi=cls._model_api_location,
            uid=uid)
        return url

    @properties.validator
    def validate(self):
        for proj in self.project:
            if self not in proj.resources:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that projects contain all the '
                                 'resources that point to them.')

    @needs_login
    def upload(self, sync=True, print_url=True):
        """Upload the resource through its containing project(s)"""
        # self.validate()
        for proj in self.project:
            proj.upload(sync, False)
        if print_url:
            try:
                print(self._url)
            except:
                print('URL error: Upload may have failed')



    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        if 'mesh' in dirty or force:
            datadict['mesh'] = dumps({
                'uid': self.mesh._json['longUid']
            })
        if 'data' in dirty or force:
            datadict['data'] = dumps([
                {
                    'location': d.location,
                    'uid': d.data._json['longUid']
                } for d in self.data
            ])
        if 'textures' in dirty or (force and hasattr(self, 'textures')):
            datadict['textures'] = dumps([
                {
                    'uid': t._json['longUid']
                } for t in self.textures
            ])
        return datadict

    def _upload_dirty(self):
        dirty = self._dirty
        # if 'project' in dirty:
        #     [p._upload() for p in self.project]
        if 'mesh' in dirty:
            self.mesh._upload()
        if 'data' in dirty:
            [d.data._upload() for d in self.data]
        if 'textures' in dirty:
            [t._upload() for t in self.textures]

    def _on_property_change(self, name, pre, post):
        if name == 'project':
            if pre is None:
                pre = []
            if post is None:
                post = []
            for proj in post:
                if proj not in pre:
                    proj.resources += [self]
            for proj in pre:
                if proj not in post:
                    proj.resources = [r for r in proj.resources
                                      if r is not self]
            if len(set(post)) != len(post):
                post_post = []
                for p in post:
                    if p not in post_post:
                        post_post += [p]
                self.project = post_post
        super()._on_property_change(name, pre, post)

    @property
    def _url(self):
        if getattr(self, '_upload_data', None) is not None:
            return self._url_view_from_uid(self._upload_data['uid'])

    @property
    @needs_login
    def url(self):
        """steno3d.com url of project if uploaded"""
        if getattr(self, '_upload_data', None) is None:
            print('Resource not uploaded')
            return
        print(self._url)

    @needs_login
    def plot(self):
        """Display the 3D representation of the content"""
        if getattr(self, '_upload_data', None) is None:
            raise Exception("Plotting failed: Resource's project not "
                            'uploaded - please upload() first.')
        return plot(self._url)


class BaseMesh(BaseResource):
    """Base class for all mesh resources. These are contained within
    each composite resources and define its structure
    """


class BaseData(BaseResource):
    """Base class for all data resources. These can be contained within
    each composite resource and define data corresponding to the mesh
    """
    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/data/{class_name}'.format(
                class_name=cls._resource_class)
        return cls.__model_api_location


class BaseTexture2D(BaseResource):
    """Base class for all texture resources. These can be contained
    within some composite resources and define data in space that gets
    mapped to the mesh.
    """
    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/texture2d/{class_name}'.format(
                class_name=cls._resource_class)
        return cls.__model_api_location
