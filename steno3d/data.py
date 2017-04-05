"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import string_types

from numpy import ndarray
import properties

from .base import BaseData
from .props import array_serializer, array_download


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh"""
    _resource_class = 'array'
    array = properties.Array(
        doc='Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int),
        serializer=array_serializer,
        deserializer=array_download(('*',), (float, int)),
    )

    order = properties.StringChoice(
        doc='Data array order, for data on grid meshes',
        choices={
            'c': ('C-STYLE', 'NUMPY', 'ROW-MAJOR', 'ROW'),
            'f': ('FORTRAN', 'MATLAB', 'COLUMN-MAJOR', 'COLUMN', 'COL')
        },
        default='c',
    )
    colormap = properties.List(
        doc='Colormap applied to data range',
        prop=properties.Color(''),
        min_length=1,
        max_length=256,
        required=False,
    )

    def __init__(self, array=None, **kwargs):
        super(DataArray, self).__init__(**kwargs)
        if array is not None:
            self.array = array

    def _nbytes(self, arr=None):
        if arr is None or (isinstance(arr, string_types) and arr == 'array'):
            arr = self.array
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('DataArray cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.observer('array')
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_array(self):
        self._validate_file_size('array', self.array)
        return True

    def _get_dirty_data(self, force=False):
        datadict = super(DataArray, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'order' in dirty or force:
            datadict['order'] = self.order
        if self.colormap is not None and 'colormap' in dirty or force:
            datadict['colormap'] = self.colormap
        return datadict

    def _get_dirty_files(self, force=False):
        files = super(DataArray, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'array' in dirty or force:
            files['array'] = self._props['array'].serialize(self.array)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataArray(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=cls._props['array'].deserialize(
                json['array'],
            )
        )
        if json.get('colormap'):
            data.colormap = json['colormap']
        return data

    @classmethod
    def _build_from_omf(cls, omf_data):
        assert omf_data.__class__.__name__ in ('ScalarData', 'MappedData')
        data = dict(
            location='N' if omf_data.location == 'vertices' else 'CC',
            data=DataArray(
                title=omf_data.name,
                description=omf_data.description,
                array=omf_data.array.array
            )
        )
        return data


class DataCategory(DataArray):
    _resource_class = 'category'  # ...? or same on the backend...?
    array = properties.Array(
        doc='Category index values at every point in the mesh',
        shape=('*',),
        dtype=(int,),
        serializer=array_serializer,
        deserializer=array_download(('*',), (int,)),
    )
    categories = properties.List(
        doc='List of string categories',
        prop=properties.String(''),
        min_length=1,
        max_length=256,
    )
    colormap = properties.List(
        doc='Colors corresponding to categories',
        prop=properties.Color(''),
        min_length=1,
        max_length=256,
    )

    @properties.validator
    def _categories_and_colormap(self):
        if len(self.categories) != len(self.colormap):
            raise ValueError('categories and colormap must be equal length')

    @properties.validator
    def _categories_and_array(self):
        if min(self.array) < 0 or max(self.array) >= len(self.categories):
            raise ValueError('indices must be >= 0 and < len(categories)')

    def _get_dirty_data(self, force=False):
        datadict = super(DataCategory, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'categories' in dirty or force:
            datadict['categories'] = self.categories
        return datadict

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataCategory(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=cls._props['array'].deserialize(
                json['array'],
            ),
            colormap=json['colormap'],
            categories=json['categories'],
        )
        return data


__all__ = ['DataArray', 'DataCategory']
