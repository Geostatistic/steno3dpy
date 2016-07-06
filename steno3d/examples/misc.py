"""mics.py contains miscellaneous files and components to supplement
Steno3D examples
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .base import BaseExample


class Images(BaseExample):
    """Class containing miscellaneous image files."""

    def example_name(self):
        return 'Images'

    def sub_directory(self):
        return 'basic'

    def filenames(self):
        return ['metal.png',
                'woodplanks.png',
                'steno3d.png',
                'steno3d_logo_text.png',
                'licenses.txt']

    def metal(self):
        """metal texture png"""
        return Images.fetch_data(filename='metal.png',
                                 download_if_missing=False,
                                 verbose=False)

    def wood(self):
        """wood texture png"""
        return Images.fetch_data(filename='woodplanks.png',
                                 download_if_missing=False,
                                 verbose=False)

    def logo(self):
        """wood texture png"""
        return Images.fetch_data(filename='steno3d.png',
                                 download_if_missing=False,
                                 verbose=False)

    def logo_with_text(self):
        """wood texture png"""
        return Images.fetch_data(filename='steno3d_logo_text.png',
                                 download_if_missing=False,
                                 verbose=False)

try:
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
