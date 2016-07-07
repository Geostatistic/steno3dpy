"""content.py contains the base class for everything users can create
in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from pprint import pformat

import properties

from .client import pause
from .client import post
from .client import put


class UserContent(properties.PropertyClass):
    """Base class for everything user creates and uploads in steno3d"""
    title = properties.String(
        'Title of the model.',
        default=''
    )
    description = properties.String(
        'Description of the model.',
        default=''
    )
    _sync = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._upload_data = None

    @properties.classproperty
    @classmethod
    def _resource_class(cls):
        """name of the class of resource"""
        if getattr(cls, '__resource_class', None) is None:
            cls.__resource_class = cls.__name__.lower()
        return cls.__resource_class

    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/{className}'.format(
                className=cls._resource_class
            )
        return cls.__model_api_location

    def _upload(self, sync=True):
        if getattr(self, '_uploading', False):
            return
        try:
            self._uploading = True
            pause()
            assert self.validate()
            self._upload_dirty()
            if getattr(self, '_upload_data', None) is None:
                self._post(
                    self._get_dirty_data(force=True),
                    self._get_dirty_files(force=True)
                )
            else:
                dirty_data = self._get_dirty_data()
                dirty_files = self._get_dirty_files()
                if len(dirty_data) > 0 or len(dirty_files) > 0:
                    self._put(dirty_data, dirty_files)
            self._mark_clean(recurse=False)
            self._sync = sync
        except Exception as err:
            if self._sync:
                print('Upload failed, turning off syncing. To restart '
                      'syncing, upload() again.')
                self._sync = False
            else:
                raise err
        finally:
            self._uploading = False

    def _get_dirty_data(self, force=False):
        dirty = self._dirty_props
        datadict = dict()
        if 'title' in dirty or force:
            datadict['title'] = self.title
        if 'description' in dirty or force:
            datadict['description'] = self.description
        return datadict

    def _get_dirty_files(self, force=False):
        return {}

    def _upload_dirty(self):
        pass

    def _on_property_change(self, name, pre, post):
        if getattr(self, '_sync', False):
            self._upload()

    def _post(self, datadict=None, files=None):
        self._client_upload(post, self._model_api_location,
                            datadict, files)

    def _put(self, datadict=None, files=None):
        pause()
        api_uid = '{mapi}/{uid}'.format(mapi=self._model_api_location,
                                        uid=self._upload_data['uid'])
        self._client_upload(put, api_uid, datadict, files)

    def _client_upload(self, request_fcn, url,
                       datadict=None, files=None):
        req = request_fcn(
            url,
            data=datadict if datadict else tuple(),
            files=files if files else tuple(),
        )
        if isinstance(req, list):
            for rq in req:
                if rq.status_code != 200:
                    try:
                        resp = pformat(rq.json())
                    except ValueError:
                        resp = rq

                    raise Exception(
                        'Upload failed: {location}'.format(
                            location=url,
                        ) +
                        '\ndata: {datadict}\nfiles: {filedict}'.format(
                            datadict=pformat(datadict),
                            filedict=pformat(files),
                        ) +
                        '\nresponse: {response}'.format(
                            response=resp,
                        )
                    )
            self._upload_data = [rq.json() for rq in req]
        else:
            if req.status_code != 200:
                try:
                    resp = pformat(req.json())
                except ValueError:
                    resp = req
                raise Exception(
                    'Upload failed: {location}'.format(
                        location=url,
                    ) +
                    '\ndata: {datadict}\nfiles: {filedict}'.format(
                        datadict=pformat(datadict),
                        filedict=pformat(files),
                    ) +
                    '\nresponse: {response}'.format(
                        response=resp,
                    )
                )
            self._upload_data = req.json()

    @property
    def _json(self):
        """Return a JSON representation of the object"""
        json = getattr(self, '_upload_data', None)
        if json is None:
            raise ValueError('JSON not available: Data not uploaded')
        return json

    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        return True

