"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

import properties

from .base import BaseData


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh"""
    _resource_class = 'array'
    array = properties.Array(
        'Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int),
        required=True
    )

    def __init__(self, array=None, **kwargs):
        super().__init__(**kwargs)
        if array is not None:
            self.array = array

    def nbytes(self, name=None):
        if name is None or name == 'array':
            return self.array.nbytes
        raise ValueError('DataArray cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name == 'array':
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)


    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        self._validate_file_size('array')
        return True

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'array' in dirty or force:
            files['array'] = self._properties['array'].serialize(self.array)
        return files

__all__ = ['DataArray']
