"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from numpy import ndarray
from traitlets import observe, validate

from .base import BaseData
from .traits import Array, StringChoices, validator


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh"""
    _resource_class = 'array'
    array = Array(
        help='Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int)
    )

    order = StringChoices(
        help='Data array order, for data on grid meshes',
        choices={
            'c': ('C-STYLE', 'NUMPY', 'ROW-MAJOR', 'ROW'),
            'f': ('FORTRAN', 'MATLAB', 'COLUMN-MAJOR', 'COLUMN', 'COL')
        },
        default_value='c',
        lowercase=True
    )

    # def __init__(self, array=None, **kwargs):
    #     super().__init__(**kwargs)
    #     if array is not None:
    #         self.array = array

    def _nbytes(self, arr=None):
        if arr is None or arr == 'array':
            arr = self.array
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('DataArray cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('array')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['new'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('array')
    def _validate_array(self, proposal):
        proposal['owner']._validate_file_size('array', proposal['value'])
        return proposal['value']

    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        if ('order' in dirty) or force:
            datadict['order'] = self.order
        return datadict

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'array' in dirty or force:
            files['array'] = self._properties['array'].serialize(self.array)
        return files

__all__ = ['DataArray']
