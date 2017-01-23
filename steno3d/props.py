from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from io import BytesIO
from tempfile import NamedTemporaryFile

import numpy as np
from requests import get
import properties


class HasSteno3DProps(properties.HasProperties):

    def __init__(self, **metadata):
        self._dirty_props = set()
        super(HasSteno3DProps, self).__init__(**metadata)

    def _get(self, name):
        value = super(HasSteno3DProps, self)._get(name)
        # Returning a copy of the list maintains backward compatibility
        # until properties has better handling of lists.
        if isinstance(value, list):
            value = [val for val in value]
        return value

    @properties.observer(properties.everything)
    def _mark_dirty(self, change):
        self._dirty_props.add(change['name'])

    def _mark_clean(self, recurse=True):
        self._dirty_props = set()
        if not recurse or getattr(self, '_inside_clean', False):
            return
        self._inside_clean = True
        try:
            props = self._dirty
            for prop in props:
                value = getattr(self, prop)
                if isinstance(value, properties.HasProperties):
                    value._mark_clean()
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if isinstance(v, properties.HasProperties):
                            v._mark_clean()
        finally:
            self._inside_clean = False

    @property
    def _dirty(self):
        if getattr(self, '_inside_dirty', False):
            return set()
        dirty_instances = set()
        self._inside_dirty = True
        try:
            props = self._non_deprecated_props()
            for prop in props:
                value = getattr(self, prop)
                if (isinstance(value, properties.HasProperties) and
                        len(value._dirty) > 0):
                    dirty_instances.add(prop)
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if (isinstance(v, properties.HasProperties) and
                                len(v._dirty) > 0):
                            dirty_instances.add(prop)
        finally:
            self._inside_dirty = False
        return self._dirty_props.union(dirty_instances)

    def _non_deprecated_props(self):
        # return {k: v for k, v in self._props.items()
        #         if not isinstance(v, Renamed)}
        return self._props


def image_download(prop, url):
    im_resp = get(url)
    if im_resp.status_code != 200:
        raise IOError('Failed to download image.')
    output = BytesIO()
    output.name = 'texture.png'
    for chunk in im_resp:
        output.write(chunk)
    output.seek(0)
    return output


FileProp = namedtuple('FileProp', ['file', 'dtype'])




def array_serializer(prop, data):
    """Convert the array data to a serialized binary format"""
    if isinstance(data.flatten()[0], np.floating):
        use_dtype = '<f4'
        nan_mask = ~np.isnan(data)
        assert np.allclose(
                data.astype(use_dtype)[nan_mask], data[nan_mask]), \
            'Converting the type should not screw things up.'
    elif isinstance(data.flatten()[0], np.integer):
        use_dtype = '<i4'
        assert (data.astype(use_dtype) == data).all(), \
            'Converting the type should not screw things up.'
    else:
        raise Exception('Must be a float or an int: {}'.format(data.dtype))

    data_file = NamedTemporaryFile('rb+', suffix='.dat')
    data.astype(use_dtype).tofile(data_file.file)
    data_file.seek(0)
    return FileProp(data_file, use_dtype)

def array_download(prop, url):
    arr_resp = get(url)
    if arr_resp.status_code != 200:
        raise IOError('Failed to download array.')
    data_file = NamedTemporaryFile()
    for chunk in arr_resp:
        data_file.write(chunk)
    data_file.seek(0)
    arr = np.fromfile(data_file.file, prop.dtype).reshape(prop.shape)
    data_file.close()
    return arr
