from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import integer_types
from six import string_types

from .client import Comms, get, needs_login
from .project import Project


def _mine(queue=10):
    cursor = ''
    more = True
    while more:
        print('Queuing {} projects...'.format(queue))
        resp = get('project/steno3ds/mine?brief=True&'
                   'num={n}&cursor={c}'.format(n=queue, c=cursor))
        rjson = resp.json()
        cursor = rjson['cursor']
        more = rjson['more']
        for proj in rjson['data']:
            yield proj


def _short_json(proj_json):
    return {'uid': proj_json['uid'],
            'title': proj_json['title'],
            'description': proj_json['description'],
            'created': proj_json['date']}


@needs_login
def all_my_projects(queue=100):
    return [_short_json(p) for p in _mine(queue)]


@needs_login
def last_n_projects(n, queue=10):
    if not isinstance(n, integer_types):
        raise ValueError('{}: n must be int'.format(n))
    projs = []
    projit = _mine(queue)
    for i in range(n):
        try:
            projs += [_short_json(next(projit))]
        except StopIteration:
            print('{n}: n > total number of projects, {p} returned'.format(
                n=n, p=len(projs)
            ))
            break
    return projs


@needs_login
def project_by_uid(uid):
    return Project._build_from_uid(uid)
    if not isinstance(uid, string_types) or len(uid) != 20:
        raise ValueError('{}: invalid uid'.format(uid))
    resp = get('project/steno3d/{uid}'.format(uid=uid))
    if resp.status_code != 200:
        raise ValueError('{}: project query failed'.format(uid))
    return Project._build_from_json(resp.json())


@needs_login
def project_by_title(title):
    if not isinstance(title, string_types):
        raise ValueError('{}: title must be string'.format(title))
    for p in _mine():
        if p['title'] == title:
            return project_by_uid(p['uid'])
    raise ValueError('{}: no project with this title found'.format(title))


@needs_login
def last_project_created():
    try:
        return project_by_uid(next(_mine())['uid'])
    except StopIteration:
        print('No projects available!')
