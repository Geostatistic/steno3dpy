"""client.py contains the functionality to link the python steno3d
client with the steno3d website
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str
from builtins import input
from functools import wraps
from time import sleep

import keyring
import requests
from six import string_types
from six.moves.urllib.parse import urlparse

from .user import User


__version__ = '0.1.6'

PRODUCTION_BASE_URL = 'https://steno3d.com/'
API_SUBPATH = 'api/'
SLEEP_TIME = .75

WELCOME_HEADER = """

Welcome to the Python client library for Steno3D!

"""

DEVKEY_PROMPT = "If you have a Steno3D developer key, please enter it here > "

WELCOME_MESSAGE = """

If you do not have a Steno3D developer key, you need to request
one from the Steno3D website in order to access the API. Please
log in to the application (if necessary) and request a new key.

{base_url}settings/developer

If you are not yet signed up, you can do that here:

{base_url}signup

When you are ready, please enter the key above, or reproduce this
prompt by calling steno3d.login().

"""

LOGIN_FAILED = """

Oh no! We could not log you in.

The API developer key that you provided could not be validated. You could:

1) Clear your keychain with `steno3d.logout()` and try again
2) Restart your Python kernel and try again
3) Check that you have the correct API key
4) Update steno3d with `pip install --upgrade steno3d`
5) Ask for <help@steno3d.com>
6) Open an issue https://github.com/3ptscience/steno3dpy/issues

"""

NOT_CONNECTED = """

Oh no! We could not connect to the Steno3D server.

Please ensure that you are:

1) connected to the Internet!
2) Can connect to Steno3D on  https://steno3d.com

If the issue persists please:

1) Ask for <help@steno3d.com>
2) Open an issue https://github.com/3ptscience/steno3dpy/issues

"""

BAD_API_KEY = """

The API developer key should be your username followed by '//' then 36
characters. If you have not requested an API key or if you have lost
your API key, please request a new one at:

{base_url}settings/developer

"""

INVALID_VERSION = """

Your version of steno3d is out of date.

{your_version}
{current_version}

Please update steno3d with `pip install --upgrade steno3d`.

"""



class _Comms(object):
    """Comms controls the interaction between the python client and the
    Steno3D website.
    """

    def __init__(self):
        self._user = None
        self._me = None
        self._base_url = PRODUCTION_BASE_URL
        self._hard_devel_key = None

    @property
    def host(self):
        """hostname of url"""
        parseresult = urlparse(self.base_url)
        return parseresult.hostname

    @property
    def url(self):
        """url endpoint for uploading"""
        return self.base_url + API_SUBPATH

    @property
    def base_url(self):
        """base url endpoint for uploading"""
        return getattr(self, '_base_url', PRODUCTION_BASE_URL)

    @base_url.setter
    def base_url(self, value):
        assert isinstance(value, string_types), \
            'Endpoint path must be a string'
        # Patch '/' onto bare URL endpoints
        if not value[-1] == '/':
            value += '/'
        # Check for HTTPS
        parsed = urlparse(value)
        if '.com' in parsed.hostname and parsed.scheme != 'https':
            raise Exception('Live endpoints require HTTPS.')

        self._base_url = value

    @property
    def devel_key(self):
        """developer key acquired from steno3d.com"""
        if getattr(self, '_hard_devel_key', None) is not None:
            return self._hard_devel_key

        key = keyring.get_password('steno3d', self.host)
        if key in {None, 'None'}:
            return None
        return str(key)

    @devel_key.setter
    def devel_key(self, value):
        if value is None:
            del self.devel_key
        else:
            keyring.set_password('steno3d', self.host, value)

    @devel_key.deleter
    def devel_key(self):
        self._hard_devel_key = None
        try:
            keyring.delete_password('steno3d', self.host)
        except (keyring.errors.PasswordDeleteError, RuntimeError):
            # Happens when the key or keychain does not exist
            pass

    def get_user(self):
        if getattr(self, '_me', None) is not None:
            return self._me
        elif getattr(self, '_user', None) is None:
            return None
        else:
            username = self._user['uid']
            email = self._user['email']
            name = self._user['name']
            url = self._user['url']
            affiliation = self._user['affiliation']
            location = self._user['location']
            self._me = User(
                username=username if username is not None else 'None',
                email=email if email is not None else 'None',
                name=name if name is not None else 'None',
                url=url if url is not None else 'None',
                affiliation=affiliation if affiliation is not None else 'None',
                location=location if location is not None else 'None',
            )
            return self._me

    def login(self, devel_key=None, skip_keychain=False, endpoint=None):
        """Login to steno3d.com to allow uploading resources

        Optional arguments:
            devel_key     - API key from steno3d.com. Prompt will appear if
                            this is not provided or saved on the keychain
            skip_keychain - Prevents loading or saving API key on the
                            keychain
            endpoint      - target site, default is steno3d.com
        """
        if not skip_keychain:
            try:
                keyring.get_password('steno3d', self.host)
            except RuntimeError:
                print('Unable to access keychain. Proceeding to login with '
                      '`skip_keychain=True`.\nYou will need to '
                      'reenter your developer API key every time you '
                      'restart the kernel.')
                self.login(devel_key, True, endpoint)
                return
        if endpoint is not None:
            self.base_url = str(endpoint)
        # Check client version first.
        try:
            resp = requests.post(
                self.url + 'client/steno3dpy',
                dict(version=__version__)
            )
        except requests.ConnectionError:
            raise Exception(NOT_CONNECTED)
        if resp.status_code == 200:
            resp_json = resp.json()
            your_ver = resp_json['your_version']
            curr_ver = resp_json['current_version']
            if resp_json['valid'] or curr_ver == '0.0.0':
                pass
            elif (your_ver.split('.')[0] == curr_ver.split('.')[0] and
                  your_ver.split('.')[1] == curr_ver.split('.')[1]):
                print(INVALID_VERSION.format(
                    your_version='Your version: ' + your_ver,
                    current_version='Current version: ' + curr_ver
                ))
            else:
                raise Exception(INVALID_VERSION.format(
                    your_version='Your version: ' + your_ver,
                    current_version='Required version: ' + curr_ver
                ))
        elif resp.status_code == 400:
            resp_json = resp.json()
            print(INVALID_VERSION.format(
                your_version='Your version: ' + __version__,
                current_version='Error: ' + resp_json['reason']
            ))
        # Set devel key next
        if devel_key is not None:
            if skip_keychain:
                self._hard_devel_key = devel_key
            else:
                self.devel_key = devel_key
        if ((skip_keychain and
             getattr(self, '_hard_devel_key', None) is None) or
                self.devel_key is None):
            print(WELCOME_MESSAGE.format(base_url=self.base_url))
            try:
                devel_key = raw_input(WELCOME_HEADER + DEVKEY_PROMPT)
            except NameError:
                devel_key = input(WELCOME_HEADER + DEVKEY_PROMPT)
            split_key = devel_key.split('//')
            if len(split_key) is not 2 or len(split_key[1]) is not 36:
                self.devel_key = None
                raise Exception(BAD_API_KEY.format(base_url=self.base_url))
            if skip_keychain:
                self._hard_devel_key = devel_key
            else:
                self.devel_key = devel_key
        # Check user
        if getattr(self, '_user', None) is None:
            try:
                resp = requests.get(
                    self.url + 'me',
                    headers={'sshKey': self.devel_key}
                )
            except requests.ConnectionError:
                raise Exception(NOT_CONNECTED)
            if resp.status_code is not 200:
                self.devel_key = None
                raise Exception(LOGIN_FAILED)
            self._user = resp.json()
        # Success
        print(
            'Welcome to Steno3D! You are logged in as @{name}'.format(
                name=self.get_user().username
            )
        )

    def logout(self):
        """Logout current user and remove API key from keyring"""
        self.devel_key = None
        self._me = None
        self._user = None


Comms = _Comms()


def needs_login(func):
    """Wrapper used around functions that need you to be logged in"""
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        if Comms.get_user() is None:
            print("Please login: 'steno3d.login()'")
        else:
            return func(self, *args, **kwargs)
    return func_wrapper


def pause():
    """Brief pause on localhost to simulate network delay"""
    if 'localhost' in Comms.url:
        sleep(SLEEP_TIME)


@needs_login
def post(url, data=None, files=None):
    """Post data and files to the steno3d online endpoint"""
    return upload(requests.post, url, data, files)


@needs_login
def put(url, data=None, files=None):
    """Put data and files to the steno3d online endpoint"""
    return upload(requests.put, url, data, files)


@needs_login
def upload(request_fcn, url, data, files):
    """Post data and files to the steno3d online endpoint"""
    data = {} if data is None else data
    files = {} if files is None else files
    filedict = {}
    for filename in files:
        if hasattr(files[filename], 'dtype'):
            filedict[filename] = files[filename].file
            filedict[filename + 'Type'] = files[filename].dtype
        else:
            filedict[filename] = files[filename]
    req = request_fcn(
        Comms.url + url,
        data=data,
        files=filedict,
        headers={'sshKey': Comms.devel_key}
    )
    for key in files:
        files[key].file.close()
    return req


def plot(url):
    """Return an IFrame plot"""
    from IPython.display import IFrame
    return IFrame(url, width='100%', height=500)
