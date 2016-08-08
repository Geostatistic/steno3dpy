from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from functools import wraps
from io import BytesIO
from os.path import isfile
from six import integer_types
from six import string_types
from six import with_metaclass
from tempfile import NamedTemporaryFile

import numpy as np
import traitlets as tr


class MetaDocTraits(tr.MetaHasTraits):

    def __new__(mcs, name, bases, classdict):
        def sphinx(trait_name, trait):
            return (
                ':param {name}: {doc}\n:type {name}: :class:`{cls}`'.format(
                    name=trait_name,
                    doc=trait.help,
                    cls=trait.__class__.__name__
                )
            )

        def is_required(trait):
            return not trait.allow_none

        doc_str = classdict.get('__doc__', '')
        req = {key: value for key, value in classdict.items()
               if isinstance(value, tr.TraitType) and is_required(value)}
        opt = {key: value for key, value in classdict.items()
               if isinstance(value, tr.TraitType) and not is_required(value)}
        if req:
            doc_str += '\n\nRequired:\n\n' + '\n'.join(
                (sphinx(key, value) for key, value in req.items())
            )
        if opt:
            doc_str += '\n\nOptional:\n\n' + '\n'.join(
                (sphinx(key, value) for key, value in opt.items())
            )
        classdict['__doc__'] = doc_str.strip()

        return super(MetaDocTraits, mcs).__new__(mcs, name, bases, classdict)


class HasDocTraits(with_metaclass(MetaDocTraits, tr.HasTraits)):
    pass


def validator(func):
    """wrapper used on validation functions to recursively validate"""
    @wraps(func)
    def func_wrapper(self):
        self._cross_validation_lock = False
        try:
            trait_dict = self.traits()
            for k in trait_dict:
                if k in self._trait_values:
                    val = getattr(self, k)
                    trait_dict[k]._validate(self, val)
                    if isinstance(val, DelayedValidator):
                        val.validate()
                elif not trait_dict[k].allow_none:
                    raise tr.TraitError('Required property not set: {}'.format(k))
        finally:
            self._cross_validation_lock = True
        return func(self)
    return func_wrapper


class DelayedValidator(HasDocTraits):

    def __init__(self, *args, **kwargs):
        super(DelayedValidator, self).__init__(*args, **kwargs)
        self._cross_validation_lock = True

    @validator
    def validate(self):
        return True


class Color(tr.TraitType):
    """A trait for rgb, hex, or string colors. Converts to rgb."""

    default_value = 'RANDOM'
    info_text = ('a color (RGB with values 0-255, hex color e.g. \'#FF0000\', '
                'string color name, or \'random\')')

    def validate(self, obj, value):
        """check if input is valid color and converts to RBG"""
        if isinstance(value, string_types):
            if value in COLORS_NAMED:
                value = COLORS_NAMED[value]
            if value.upper() == 'RANDOM':
                value = COLORS_20[np.random.randint(0, 20)]
            value = value.upper().lstrip('#')
            if len(value) == 3:
                value = ''.join(v*2 for v in value)
            if len(value) != 6:
                self.error(obj, value)
            try:
                value = [
                    int(value[i:i + 6 // 3], 16) for i in range(0, 6, 6 // 3)
                ]
            except ValueError:
                self.error(obj, value)
        if not isinstance(value, (list, tuple)):
                self.error(obj, value)
        if len(value) != 3:
                self.error(obj, value)
        for v in value:
            if not isinstance(v, integer_types) or not 0 <= v <= 255:
                self.error(obj, value)
        return tuple(value)


class StringChoices(tr.Enum):
    """A trait for strings, where you can map several values to one"""

    def __init__(self, choices={}, lowercase=False, strip=' ', **metadata):
        if not isinstance(choices, (list, tuple, dict)):
            raise tr.TraitError('choices must be a list, tuple, or dict')
        if isinstance(choices, (list, tuple)):
            choices = {v: v for v in choices}
        for k, v in choices.items():
            if not isinstance(v, (list, tuple)):
                choices[k] = [v]
        for k, v in choices.items():
            if not isinstance(k, string_types):
                raise tr.TraitError('choices must be strings')
            for val in v:
                if not isinstance(val, string_types):
                    raise tr.TraitError('choices must be strings')
        self.lowercase = lowercase
        self.strip = strip
        self.choices = choices
        super(StringChoices, self).__init__([v for v in choices], **metadata)

    def validate(self, obj, value):
        """check that input is string and in choices, if applicable"""
        if not isinstance(value, string_types):
            self.error(obj, value)
        if self.strip is not None:
            value = value.strip(self.strip)
        if self.choices is not None and len(self.choices) != 0:
            for k, v in self.choices.items():
                if (value.upper() == k.upper() or
                        value.upper() in [_.upper() for _ in v]):
                    return k.lower() if self.lowercase else k
            self.error(obj, value)
        return value.lower() if self.lowercase else value


class Image(tr.TraitType):
    """A trait for PNG images"""

    info_text = 'a PNG image file'

    def validate(self, obj, value):
        """checks that image file is PNG and gets a copy"""
        try:
            import png
        except:
            raise ImportError('Error importing png module: '
                              '`pip install pypng`')

        if getattr(value, '__valid__', False):
            return value

        try:
            if hasattr(value, 'read'):
                png.Reader(value).validate_signature()
            else:
                with open(value, 'rb') as v:
                    png.Reader(v).validate_signature()
        except Exception:
            self.error(obj, value)

        output = BytesIO()
        output.name = 'texture.png'
        output.__valid__ = True
        if hasattr(value, 'read'):
            fp = value
            fp.seek(0)
        else:
            fp = open(value, 'rb')
        output.write(fp.read())
        output.seek(0)
        fp.close()
        return output


FileProp = namedtuple('FileProp', ['file', 'dtype'])


class Array(tr.TraitType):
    """A trait for serializable float or int arrays"""

    def __init__(self, shape=('*',), dtype=(float, int), **metadata):
        if not isinstance(shape, tuple):
            raise tr.TraitError("{}: Invalid shape - must be a tuple "
                                "(e.g. ('*',3) for an array of length-3 "
                                "arrays)".format(shape))
        for s in shape:
            if s != '*' and not isinstance(s, integer_types):
                raise tr.TraitError("{}: Invalid shape - values "
                                    "must be '*' or int".format(shape))
        self.shape = shape

        if not isinstance(dtype, (list, tuple)):
            dtype = (dtype,)
        if (float not in dtype and
                len(set(dtype).intersection(integer_types)) == 0):
            raise tr.TraitError("{}: Invalid dtype - must be int "
                                "and/or float".format(dtype))
        self.dtype = dtype
        super(Array, self).__init__(**metadata)

    def info(self):
        return 'a list or numpy array of {type} with shape {shp}'.format(
            type=', '.join([str(t) for t in self.dtype]),
            shp=self.shape
        )

    def validate(self, obj, value):
        """Determine if array is valid based on shape and dtype"""
        if not isinstance(value, (list, np.ndarray)):
            self.error(obj, value)
        value = np.array(value)
        if (value.dtype.kind == 'i' and
                len(set(self.dtype).intersection(integer_types)) == 0):
            self.error(obj, value)
        if value.dtype.kind == 'f' and float not in self.dtype:
            self.error(obj, value)
        if len(self.shape) != value.ndim:
            self.error(obj, value)
        for i, s in enumerate(self.shape):
            if s != '*' and value.shape[i] != s:
                self.error(obj, value)
        return value

    def serialize(self, data):
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
        data.astype(use_dtype).tofile(data_file.name)
        data_file.seek(0)
        return FileProp(data_file, use_dtype)


class Vector(Array):
    """A trait for 3D vectors"""

    def __init__(self, **metadata):
        super(Vector, self).__init__(shape=(3,), dtype=float, **metadata)

    def validate(self, obj, value):
        if isinstance(value, string_types):
            if value.upper() == 'X':
                value = [1., 0, 0]
            if value.upper() == 'Y':
                value = [0., 1, 0]
            if value.upper() == 'Z':
                value = [0., 0, 1]
        return super(Vector, self).validate(obj, value)


class KeywordInstance(tr.Instance):
    """An instance trait that can be constructed with only a keyword dict"""

    def __init__(self, klass=None, args=(), kw=None, **metadata):
        if klass is None:
            raise tr.TraitError('KeywordInstance klass cannot be None')
        super(KeywordInstance, self).__init__(klass, args, kw, **metadata)

    def validate(self, obj, value):
        if isinstance(value, self.klass):
            return value
        if isinstance(value, dict):
            try:
                return self.klass(**value)
            except:
                self.error(obj, value)
        try:
            return self.klass(value)
        except:
            self.error(obj, value)

    def info(self):
        if isinstance(self.klass, string_types):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = tr.class_of(klass)
        result = result + ' or a keyword dictionary to construct ' + result
        if self.allow_none:
            return result + ' or None'
        return result

class Repeated(tr.List):
    """A list trait that creates a length-1 list if given an instance"""

    def validate(self, obj, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        return super(Repeated, self).validate(obj, value)



COLORS_20 = [
    '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
    '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
    '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
    '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5'
]

COLORS_NAMED = dict(
    aliceblue="F0F8FF", antiquewhite="FAEBD7", aqua="00FFFF",
    aquamarine="7FFFD4", azure="F0FFFF", beige="F5F5DC",
    bisque="FFE4C4", black="000000", blanchedalmond="FFEBCD",
    blue="0000FF", blueviolet="8A2BE2", brown="A52A2A",
    burlywood="DEB887", cadetblue="5F9EA0", chartreuse="7FFF00",
    chocolate="D2691E", coral="FF7F50", cornflowerblue="6495ED",
    cornsilk="FFF8DC", crimson="DC143C", cyan="00FFFF",
    darkblue="00008B", darkcyan="008B8B", darkgoldenrod="B8860B",
    darkgray="A9A9A9", darkgrey="A9A9A9", darkgreen="006400",
    darkkhaki="BDB76B", darkmagenta="8B008B", darkolivegreen="556B2F",
    darkorange="FF8C00", darkorchid="9932CC", darkred="8B0000",
    darksalmon="E9967A", darkseagreen="8FBC8F", darkslateblue="483D8B",
    darkslategray="2F4F4F", darkslategrey="2F4F4F", darkturquoise="00CED1",
    darkviolet="9400D3", deeppink="FF1493", deepskyblue="00BFFF",
    dimgray="696969", dimgrey="696969", dodgerblue="1E90FF",
    irebrick="B22222", floralwhite="FFFAF0", forestgreen="228B22",
    fuchsia="FF00FF", gainsboro="DCDCDC", ghostwhite="F8F8FF",
    gold="FFD700", goldenrod="DAA520", gray="808080",
    grey="808080", green="008000", greenyellow="ADFF2F",
    honeydew="F0FFF0", hotpink="FF69B4", indianred="CD5C5C",
    indigo="4B0082", ivory="FFFFF0", khaki="F0E68C",
    lavender="E6E6FA", lavenderblush="FFF0F5", lawngreen="7CFC00",
    lemonchiffon="FFFACD", lightblue="ADD8E6", lightcoral="F08080",
    lightcyan="E0FFFF", lightgoldenrodyellow="FAFAD2", lightgray="D3D3D3",
    lightgrey="D3D3D3", lightgreen="90EE90", lightpink="FFB6C1",
    lightsalmon="FFA07A", lightseagreen="20B2AA", lightskyblue="87CEFA",
    lightslategray="778899", lightslategrey="778899", lightsteelblue="B0C4DE",
    lightyellow="FFFFE0", lime="00FF00", limegreen="32CD32",
    linen="FAF0E6", magenta="FF00FF", maroon="800000",
    mediumaquamarine="66CDAA", mediumblue="0000CD", mediumorchid="BA55D3",
    mediumpurple="9370DB", mediumseagreen="3CB371", mediumslateblue="7B68EE",
    mediumspringgreen="00FA9A", mediumturquoise="48D1CC",
    mediumvioletred="C71585", midnightblue="191970", mintcream="F5FFFA",
    mistyrose="FFE4E1", moccasin="FFE4B5", navajowhite="FFDEAD",
    navy="000080", oldlace="FDF5E6", olive="808000",
    olivedrab="6B8E23", orange="FFA500", orangered="FF4500",
    orchid="DA70D6", palegoldenrod="EEE8AA", palegreen="98FB98",
    paleturquoise="AFEEEE", palevioletred="DB7093", papayawhip="FFEFD5",
    peachpuff="FFDAB9", peru="CD853F", pink="FFC0CB",
    plum="DDA0DD", powderblue="B0E0E6", purple="800080",
    rebeccapurple="663399", red="FF0000", rosybrown="BC8F8F",
    royalblue="4169E1", saddlebrown="8B4513", salmon="FA8072",
    sandybrown="F4A460", seagreen="2E8B57", seashell="FFF5EE",
    sienna="A0522D", silver="C0C0C0", skyblue="87CEEB",
    slateblue="6A5ACD", slategray="708090", slategrey="708090",
    snow="FFFAFA", springgreen="00FF7F", steelblue="4682B4",
    tan="D2B48C", teal="008080", thistle="D8BFD8",
    tomato="FF6347", turquoise="40E0D0", violet="EE82EE",
    wheat="F5DEB3", white="FFFFFF", whitesmoke="F5F5F5",
    yellow="FFFF00", yellowgreen="9ACD32"
)
