"""options.py defines the base option classes for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps

from .traits import Bool, Color, Float, HasSteno3DTraits


class Options(HasSteno3DTraits):
    """Generic options for all steno3d resources"""

    @property
    def _json(self):
        """returns json representation of options"""
        opts_json = {}
        for key in self.trait_names():
            opts_json[key] = getattr(self, key)
        return dumps(opts_json)


class ColorOptions(Options):
    """Options related to resource display color"""
    color = Color(
        help='Solid color',
        default_value='random'
    )
    opacity = Float(
        help='Opacity',
        default_value=1.,
        min=0.,
        max=1.
    )


class MeshOptions(Options):
    """Options related to mesh display"""
    wireframe = Bool(
        help='Wireframe',
        default_value=False
    )
