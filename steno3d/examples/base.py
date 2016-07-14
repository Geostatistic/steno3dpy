"""base.py sets up BaseExample class that allows examples to be accessed
as properties at the class level
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os import mkdir
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os.path import realpath
from os.path import sep

from future.utils import with_metaclass
from requests import get
from six import string_types
from zipfile import ZipFile


class exampleproperty(object):
    """wrapper that sets class method as saved property"""

    def __init__(self, func):
        self.func = classmethod(func)
        self.propname = '_' + func.__name__

    def __get__(self, cls, owner):
        if getattr(owner, self.propname, None) is None:
            setattr(owner, self.propname, self.func.__get__(None, owner)())
        return getattr(owner, self.propname)


class exampleoutput(object):
    """wrapper that sets class method to remove saved properties"""

    def __init__(self, func, directory):
        self.func = classmethod(func)
        self._directory = ['_' + prop for prop in directory]
        self._stash = [None for prop in directory]

    def __get__(self, cls, owner):
        def _output():
            """return the original function surrounded by stash and unstash"""
            self.stash(owner)
            out = self.func.__get__(None, owner)()
            self.unstash(owner)
            return out
        return _output

    def stash(self, owner):
        """stash saved properties during example output"""
        for i, prop in enumerate(self._directory):
            self._stash[i] = getattr(owner, prop, None)
            setattr(owner, prop, None)

    def unstash(self, owner):
        """unstash saved properties after example output"""
        for i, prop in enumerate(self._directory):
            setattr(owner, prop, self._stash[i])


class _ExampleMetaClass(type):
    """metaclass that wraps every function with exampleproperty()"""

    def __new__(mcs, name, bases, attrs):
        if name not in ('BaseExample', 'Images'):
            assert ('get_resources' in attrs and
                    callable(attrs['get_resources'])), \
                'Example {cls} class must have method get_resources()'.format(
                    cls=name
                )
            assert ('get_project' in attrs and
                    callable(attrs['get_project'])), \
                'Example class {cls} must have method get_project()'.format(
                    cls=name
                )

        example_directory = []
        for attr in attrs:
            value = attrs[attr]
            if not attr.startswith('get_') and not attr == 'fetch_data' and \
                    callable(value):
                attrs[attr] = exampleproperty(value)
                example_directory.append(attr)

        for attr in attrs:
            value = attrs[attr]
            if attr.startswith('get_') and callable(value):
                attrs[attr] = exampleoutput(value, example_directory)

        return type.__new__(mcs, name, bases, attrs)


class BaseExample(with_metaclass(_ExampleMetaClass, object)):
    """basic class that all examples inherit from"""

    def __init__(self, *args, **kwargs):
        raise TypeError('Examples cannot be instantiated. Please access '
                        'the properties directly.')

    def example_name(self):
        return 'BaseExample'

    def data_directory(self):
        """path to directory containing all assets"""
        return sep.join([expanduser('~'), '.steno3d_python_assets'])

    def sub_directory(self):
        return self.example_name.lower()

    def filenames(self):
        return []

    def data_url(self):
        return 'https://storage.googleapis.com/steno3d-examples'

    @classmethod
    def fetch_data(cls, directory=None, download_if_missing=True,
                   filename=None, verbose=True):
        if filename is not None and not isinstance(filename, string_types):
            raise ValueError('filename: must be the name of one file')
        if cls.filenames == []:
            raise ValueError('Example does not require any files')
        if directory is not None and not isinstance(directory, string_types):
            raise ValueError('directory: must be the name of a directory')
        if directory is not None:
            directory = realpath(expanduser(directory))
            if not isdir(directory):
                raise ValueError(
                    '{}: directory does not exist'.format(directory)
                )
            cls._data_directory = directory
        if verbose:
            print('Fetching data...')
        destination = sep.join([cls.data_directory, cls.sub_directory])
        archive = sep.join([destination, cls.sub_directory + '.zip'])
        if download_if_missing and not exists(cls.data_directory):
            mkdir(cls.data_directory)
        if download_if_missing and not exists(destination):
            mkdir(destination)
        if verbose:
            print('Destination: ' + destination)
        filenames = cls.filenames if filename is None else [filename]
        for fname in filenames:
            if verbose:
                print('    Fetching: ' + fname)
            destination_file = sep.join([destination, fname])
            if exists(destination_file):
                if verbose:
                    print('        Local copy found')
                if filename is not None:
                    return destination_file
                continue
            if not exists(archive) and download_if_missing:
                if verbose:
                    print('        Downloading archive...')
                url = '/'.join([cls.data_url, cls.sub_directory + '.zip'])
                resp = get(url, stream=True)
                if resp.status_code != 200:
                    raise IOError('Error downloading {exclass} data: '
                                  '{archfile}'.format(
                                    exclass=cls.example_name,
                                    archfile=archive
                                  ))
                with open(archive, 'wb') as arch:
                    for chunk in resp:
                        arch.write(chunk)
                if verbose:
                    print('        Archive downloaded successfully')
            if exists(archive):
                if verbose:
                    print('        Local archive found: extracting...')
                try:
                    zf = ZipFile(archive)
                    zf.extract(fname, destination)
                    if verbose:
                        print('        File extracted successfully')
                    if filename is not None:
                        return destination_file
                except KeyError:
                    raise IOError('Required file(s) not found in '
                                  'archive. Archive file may be out of '
                                  'date. Please delete archive and '
                                  '{exclass}.fetch_data() again: '
                                  '{archfile}'.format(
                                    exclass=cls.example_name,
                                    archfile=archive
                                  ))
                continue
            raise IOError('Required file(s) not found - please call '
                          '{exclass}.fetch_data() to download and '
                          'save to a default folder in your home '
                          'directory or {exclass}.'
                          'fetch_data(directory=your_local_directory) '
                          'to set an alternative local directory.'.format(
                            exclass=cls.example_name
                          ))
