# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.exceptions import SecurityError
from falcon_oas.oas.security import AccessControl

user = object()


def session_user_loader(value, scopes, request):
    if value is None:
        return None
    return {'user': user, 'none': None, '1': True, '0': False}[value]


def api_key_validator(value, scopes, request):
    return value == 'secret'


security_schemes = {
    'session': (
        {'type': 'apiKey', 'name': 'session', 'in': 'cookie'},
        session_user_loader,
    ),
    'api_key': (
        {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'},
        api_key_validator,
    ),
    'http': ({'type': 'http', 'scheme': 'basic'}, None),
    'oauth2': ({'type': 'oauth2', 'flows': {}}, None),
    'openIdConnect': ({'type': 'openIdConnect', 'openIdConnectUrl': ''}, None),
}


@pytest.fixture
def access_control():
    return AccessControl(security_schemes)


def test_without_security_schemes(mocker):
    access_control = AccessControl({})
    request = mocker.MagicMock()
    operation = {'security': [{'api_key': []}]}

    assert access_control.handle(request, operation) is None


def test_without_security(mocker, access_control):
    request = mocker.MagicMock()
    operation = {'security': []}

    assert access_control.handle(request, operation) is None


@pytest.mark.parametrize(
    'security,parameters,expected',
    [
        ([{'session': []}], {'cookie': {'session': 'user'}}, user),
        (
            [{'session': [], 'api_key': []}],
            {'cookie': {'session': 'user'}, 'header': {'X-API-Key': 'secret'}},
            user,
        ),
        (
            [{'session': []}, {'api_key': []}],
            {'cookie': {'session': 'user'}, 'header': {'X-API-Key': 'bad'}},
            user,
        ),
        (
            [{'session': []}, {'api_key': []}],
            {'cookie': {'session': 'none'}, 'header': {'X-API-Key': 'secret'}},
            None,
        ),
    ],
)
def test_success(mocker, access_control, security, parameters, expected):
    request = mocker.MagicMock(**parameters)
    operation = {'security': security}

    assert access_control.handle(request, operation) is expected


@pytest.mark.parametrize(
    'security,parameters',
    [
        ([{'session': []}], {'cookie': {}}),
        ([{'session': []}], {'cookie': {'session': 'none'}}),
        (
            [{'session': [], 'api_key': []}],
            {'cookie': {'session': '0'}, 'header': {'X-API-Key': 'secret'}},
        ),
        (
            [{'session': [], 'api_key': []}],
            {'cookie': {'session': 'user'}, 'header': {'X-API-Key': 'bad'}},
        ),
    ],
)
def test_security_error(mocker, access_control, security, parameters):
    request = mocker.MagicMock(**parameters)
    operation = {'security': security}

    with pytest.raises(SecurityError):
        access_control.handle(request, operation)


def test_unknown_security_scheme_name(mocker, access_control):
    request = mocker.MagicMock()
    operation = {'security': [{'unknown': []}]}

    assert access_control.handle(request, operation) is None


@pytest.mark.parametrize(
    'security_scheme_type', ['http', 'oauth2', 'openIdConnect']
)
def test_unsupported_security_scheme_type(mocker, security_scheme_type):
    access_control = AccessControl(
        {'test': ({'type': security_scheme_type}, None)}
    )
    request = mocker.MagicMock()
    operation = {'security': [{'test': []}]}

    assert access_control.handle(request, operation) is None
