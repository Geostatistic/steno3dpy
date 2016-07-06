"""texture.py contains the texture resource structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from collections import namedtuple
from io import BytesIO
from json import dumps

import properties

from .base import BaseTexture2D


FileProp = namedtuple('FileProp', ['file', 'dtype'])


class Texture2DImage(BaseTexture2D):
    """Contains an image that can be mapped to a 2D surface"""

    _resource_class = 'image'

    O = properties.Vector(
        'Origin of the texture',
        required=True
    )
    U = properties.Vector(
        'U axis of the texture',
        required=True
    )
    V = properties.Vector(
        'V axis of the texture',
        required=True
    )
    image = properties.Image(
        'Image file',
        required=True
    )

    def nbytes(self, name=None):
        if name is None or name == 'image':
            self.image.seek(0)
            return len(self.image.read())
        raise ValueError('Texture2DImage cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name == 'image':
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.O.nV != 1 or self.U.nV != 1 or self.V.nV != 1:
            raise ValueError('O, U, and V must each be only one vector')
        self._validate_file_size('image')
        return True

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'image' in dirty or force:
            self.image.seek(0)
            copy = BytesIO()
            copy.name = 'texture_copy.png'
            copy.write(self.image.read())
            copy.seek(0)
            files['image'] = FileProp(copy, 'png')
        return files

    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        # datadict = dict()
        if ('O' in dirty or 'U' in dirty or 'V' in dirty) or force:
            datadict['OUV'] = dumps(dict(
                O=[self.O[0][0], self.O[0][1], self.O[0][2]],
                U=[self.U[0][0], self.U[0][1], self.U[0][2]],
                V=[self.V[0][0], self.V[0][1], self.V[0][2]],
            ))
        return datadict

    def _repr_png_(self):
        """For IPython display"""
        if self.image is None:
            return None
        self.image.seek(0)
        return self.image.read()


__all__ = ['Texture2DImage']
