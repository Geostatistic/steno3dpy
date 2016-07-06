"""There are parser modules available for Steno3D to read certain file
types. When a parser module is imported, the available parsers appear
inside `steno3d.parsers`.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import expanduser as _expanduser
from os.path import isfile as _isfile
from os.path import realpath as _realpath

from future.utils import with_metaclass as _with_metaclass
from properties import PropertyClass as _PropertyClass
from properties import String as _String
from six import string_types as _string_types


class _ParserMetaClass(type):
    """Metaclass to ensure Parser classes fit the requried format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != 'BaseParser':
            assert 'extensions' in attrs, \
                "You must give the `extensions` that are supported by the " \
                "{name} parser, e.g. ('obj',)".format(name=name)
            exts = attrs['extensions']
            assert isinstance(exts, tuple) and len(exts) > 0, \
                'The `extensions` in the {name} parser must be a tuple of ' \
                'supported extensions'.format(name=name)
            for ext in exts:
                assert isinstance(ext, _string_types), \
                    'Extensions in the {name} parser must be ' \
                    'strings'.format(name=name)
            assert '__init__' not in attrs, \
                "The BaseParser __init__ function takes the file_name and " \
                "any additional keyword input. Please perform other " \
                "initialization tasks for the {name} parser in " \
                "_initialize()".format(name=name)
            assert 'parse' in attrs and callable(attrs['parse']), \
                "Parser class {name} must contain a parse() method"
        new_class = super(_ParserMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class _BaseParserMetaClass(_ParserMetaClass,
                           _PropertyClass.__class__):
    """Augmented metaclass for parsers, inherits from properties
    metaclass
    """


class BaseParser(_with_metaclass(_BaseParserMetaClass,
                                 _PropertyClass)):
    """Base class for Steno3D parser objects"""

    extensions = (None,)
    file_name = _String(
        'The main file to parse',
        required=True
    )

    def __init__(self, file_name, **kwargs):
        super(BaseParser, self).__init__(**kwargs)
        if self.extensions[0] is None:
            raise NotImplementedError(
                'Please use the specific parser corresponding to your '
                'file type or `AllParsers`, not `BaseParser`'
            )
        self.file_name = self._validate_file(file_name)
        self._initialize()

    def _validate_file(self, file_name):
        """function _validate_file

        Input:
            file_name - The file to be validated

        Output:
            validated file_name

        _validate_file verifies the file exists and the extension matches
        the parser extension(s) before proceeding. This hook can be
        overwritten to remove or perform different file checks as long as
        it returns the file_name.
        """
        if not isinstance(file_name, _string_types):
            raise IOError('{}: file_name must be a string'.format(file_name))
        file_name = _realpath(_expanduser(file_name))
        if not _isfile(file_name):
            raise IOError('{}: File not found.'.format(file_name))
        if file_name.split('.')[-1] not in self.extensions:
            raise IOError('{name}: Unsupported extension. Supported '
                          'extensions are {exts}'.format(
                             name=file_name,
                             exts='(' + ', '.join(self.extensions) + ')'
                          ))
        return file_name

    def _initialize(self):
        """function _initialize

        _initialize is a hook that is called during parser __init__. The
        BaseParser sets the file_name and any additional keyword
        arguments, but _initialize can be overwritten to perform any
        additional startup tasks
        """

    def parse(self, project=None, **kwargs):
        """function parse

        Optional input:
            project - Preexisting project to add resources to. If not
                      provided, a new project will be created

        Output:
            tuple of project(s) parsed from file_name
        """
        raise NotImplementedError()

    def export(self, project, **kwargs):
        """function export

        Input:
            project - Steno3D project to be exported

        Output:
            file of the supported extension type
        """
        raise NotImplementedError()


class _AllParserMetaClass(type):
    """Metaclass to ensure Director classes fit the requried format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != 'AllParsers':
            assert name.startswith('AllParsers_'), \
                "Parser classes that inherit 'AllParsers' such as {name} " \
                "must have names that start with " \
                "'AllParsers_'".format(name=name)
            assert 'extensions' in attrs, \
                "{name} must contain a dictionary of extensions and " \
                "parsers".format(name=name)
            assert isinstance(attrs['extensions'], dict), \
                "{name} extensions must be a dictionary of extensions and " \
                "supporting parser".format(name=name)
            for ext in attrs['extensions']:
                assert isinstance(ext, _string_types), \
                    'Extensions in {name} must be strings'.format(name=name)
                assert issubclass(type(attrs['extensions'][ext]),
                                  _BaseParserMetaClass), \
                    'Extensions in {name} must direct to a ' \
                    'Parser class'.format(name=name)
        new_class = super(_AllParserMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class _BaseAllParserMetaClass(_AllParserMetaClass,
                              _PropertyClass.__class__):
    """Augmented metaclass for parser Directors, inherits from
    properties metaclass
    """


class AllParsers(_with_metaclass(_BaseAllParserMetaClass,
                                 _PropertyClass)):
    """Base class for Steno3D parser objects that parse all
    available file types
    """

    def __new__(cls, filename, **kwargs):
        if getattr(cls, 'extensions', None) is None:
            cls.extensions = dict()
            parser_keys = [
                k for k in globals()
                if (
                    k != '_BaseParser' and
                    issubclass(type(globals()[k]), _BaseParserMetaClass)
                )
            ]
            for k in parser_keys:
                for ext in globals()[k].extensions:
                    if ext not in cls.extensions:
                        cls.extensions[ext] = globals()[k]
                    elif issubclass(type(cls.extensions[ext]),
                                    _BaseParserMetaClass):
                        cls.extensions[ext] = (cls.extensions[ext].__name__ +
                                               ', ' + globals()[k].__name__)
                    else:
                        cls.extensions[ext] = (cls.extensions[ext] +
                                               ', ' + globals()[k].__name__)

        for ext in cls.extensions:
            if filename.split('.')[-1] == ext:
                if not issubclass(type(cls.extensions[ext]),
                                  _BaseParserMetaClass):
                    raise ValueError(
                        '{ext}: file type supported by more than one parser. '
                        'Please specify one of ({parsers})'.format(
                            ext=ext,
                            parsers=cls.extensions[ext]
                        )
                    )
                return cls.extensions[ext](filename, **kwargs)

        raise ValueError(
            '{bad}: unsupported file extensions. Must be in ({ok})'.format(
                bad=filename.split('.')[-1],
                ok=', '.join(list(cls.extensions))
            )
        )

try:
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
