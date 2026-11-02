"""Tests de la configuración LDAP/AD por variables de entorno."""
import pytest

from auth.auth_settings import get_ad_settings


ENV_NAMES = [
    'PANELAPP_LDAP_DOMAIN',
    'PANELAPP_LDAP_URIS',
    'PANELAPP_LDAP_LOGIN_FORMAT',
    'PANELAPP_LDAP_NETBIOS_NAME',
    'PANELAPP_LDAP_ENCRYPT_CONNECTIONS',
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def _set_required(monkeypatch, domain='local.zabik',
                  uris='ldaps://a.local.zabik:636,ldaps://b.local.zabik:636'):
    monkeypatch.setenv('PANELAPP_LDAP_DOMAIN', domain)
    monkeypatch.setenv('PANELAPP_LDAP_URIS', uris)


def test_missing_domain():
    with pytest.raises(RuntimeError, match='PANELAPP_LDAP_DOMAIN'):
        get_ad_settings()


def test_missing_uris(monkeypatch):
    monkeypatch.setenv('PANELAPP_LDAP_DOMAIN', 'local.zabik')
    with pytest.raises(RuntimeError, match='PANELAPP_LDAP_URIS'):
        get_ad_settings()


def test_full_config(monkeypatch):
    _set_required(monkeypatch)
    monkeypatch.setenv('PANELAPP_LDAP_LOGIN_FORMAT', 'netbios')
    monkeypatch.setenv('PANELAPP_LDAP_NETBIOS_NAME', 'DOMGSMNT')
    monkeypatch.setenv('PANELAPP_LDAP_ENCRYPT_CONNECTIONS', 'true')

    assert get_ad_settings() == {
        'domain': 'local.zabik',
        'ldap_uris': [
            'ldaps://a.local.zabik:636',
            'ldaps://b.local.zabik:636',
        ],
        'encrypt_connections': True,
        'netbios_name': 'DOMGSMNT',
        'login_format': 'netbios',
    }


@pytest.mark.parametrize('uris, expected', [
    (
        'ldaps://a:636;ldaps://b:636',
        ['ldaps://a:636', 'ldaps://b:636'],
    ),
    (
        '["ldaps://a:636", "ldaps://b:636"]',
        ['ldaps://a:636', 'ldaps://b:636'],
    ),
])
def test_uris_formats(monkeypatch, uris, expected):
    _set_required(monkeypatch, uris=uris)
    assert get_ad_settings()['ldap_uris'] == expected


def test_uris_empty(monkeypatch):
    _set_required(monkeypatch, uris=' , ; ')
    with pytest.raises(RuntimeError, match='PANELAPP_LDAP_URIS'):
        get_ad_settings()


@pytest.mark.parametrize('value, expected', [
    ('true', True),
    ('TRUE', True),
    ('1', True),
    ('yes', True),
    ('false', False),
    ('0', False),
    ('no', False),
    ('', False),
])
def test_encrypt_connections(monkeypatch, value, expected):
    _set_required(monkeypatch)
    monkeypatch.setenv('PANELAPP_LDAP_ENCRYPT_CONNECTIONS', value)
    assert get_ad_settings()['encrypt_connections'] is expected


def test_encrypt_connections_invalid(monkeypatch):
    _set_required(monkeypatch)
    monkeypatch.setenv('PANELAPP_LDAP_ENCRYPT_CONNECTIONS', 'quizas')
    with pytest.raises(RuntimeError, match='PANELAPP_LDAP_ENCRYPT_CONNECTIONS'):
        get_ad_settings()


def test_login_format_derived_upn(monkeypatch):
    _set_required(monkeypatch, domain='local.zabik')
    assert get_ad_settings()['login_format'] == 'upn'


def test_login_format_derived_netbios(monkeypatch):
    _set_required(monkeypatch, domain='DOMGSMNT')
    assert get_ad_settings()['login_format'] == 'netbios'


def test_login_format_netbios_name(monkeypatch):
    _set_required(monkeypatch, domain='local.zabik')
    monkeypatch.setenv('PANELAPP_LDAP_NETBIOS_NAME', 'DOMGSMNT')
    settings = get_ad_settings()
    assert settings['login_format'] == 'netbios'
    assert settings['netbios_name'] == 'DOMGSMNT'


def test_login_format_invalid(monkeypatch):
    _set_required(monkeypatch)
    monkeypatch.setenv('PANELAPP_LDAP_LOGIN_FORMAT', 'kerberos')
    with pytest.raises(RuntimeError, match='PANELAPP_LDAP_LOGIN_FORMAT'):
        get_ad_settings()
