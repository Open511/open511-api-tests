from unittest import TestCase
from urllib import urlencode
from urlparse import urljoin

from lxml import etree

import open511_validator

API_URL = None
TEST_ENDPOINT_URL = None
USE_DJANGO_TEST_CLIENT = False
EVENTS_URL = None

DjangoTestClient = None

NSMAP = {
    'gml': 'http://www.opengis.net/gml',
}

def set_options(api_url, test_endpoint_url, use_django_test_client=False):
    global API_URL, TEST_ENDPOINT_URL, EVENTS_URL, USE_DJANGO_TEST_CLIENT, DjangoTestClient, _api_endpoint_command
    API_URL = api_url
    TEST_ENDPOINT_URL = test_endpoint_url
    USE_DJANGO_TEST_CLIENT = use_django_test_client
    if use_django_test_client:
        from django.test.client import Client as DjangoTestClient
        try:
            from open511.views.test_endpoint import execute_test_endpoint_command as _api_endpoint_command
        except ImportError:
            if test_endpoint_url is None:
                raise

    EVENTS_URL = _get_events_url(api_url)

def _get_events_url(api_url):
    if USE_DJANGO_TEST_CLIENT:
        resp = DjangoTestClient().get(api_url, HTTP_ACCEPT='application/xml')
    else:
        resp = requests.get(api_url, headers={'Accept': 'application/xml'})
    discovery = etree.fromstring(resp.content)
    assert discovery.tag == 'open511'
    event_service = discovery.xpath('services/service[link[@rel="service_type"][@href = "http://open511.org/services/events/"]]')[0]
    event_url = event_service.xpath('link[@rel="self"]', namespaces=NSMAP)[0].get('href')
    return urljoin(api_url, event_url)

def _api_endpoint_command(command, **kwargs):
    data = dict(command=command)
    data.update(kwargs)
    post = DjangoTestClient().post if USE_DJANGO_TEST_CLIENT else requests.post
    assert post(TEST_ENDPOINT_URL, data=data).status_code == 200

class BaseCase(TestCase):

    @classmethod
    def load(cls, xml):
        _api_endpoint_command('load', xml=xml)

    def api_endpoint_command(self, command, **kwargs):
        return _api_endpoint_command(command, **kwargs)

    @classmethod
    def setUpClass(cls):
        _api_endpoint_command('clear')

    @classmethod
    def tearDownClass(cls):
        _api_endpoint_command('clear')        

    def get(self, url, headers={}):
        if USE_DJANGO_TEST_CLIENT:
            cgi_headers = dict(
                ('HTTP_' + key.upper().replace('-', '_'), value)
                for key, value in headers.items()
            )
            return DjangoTestClient().get(url, **cgi_headers)
        else:
            return requests.get(url, headers=headers)

    def get_events(self, url=None, **kwargs):
        params = {
            'jurisdiction': 'test.open511.org'
        }
        if url is not None and 'jurisdiction=test.open511.org' in url:
            params = {}
        headers = {
            'Accept': 'application/xml'
        }
        headers.update(kwargs.pop('headers', {}))
        params.update(kwargs)
        full_url = EVENTS_URL
        if url:
            full_url = urljoin(full_url, url)
        full_url += '&' if '?' in full_url else '?'
        full_url += urlencode(params)
        resp = self.get(full_url, headers=headers)
        assert resp.status_code == 200
        open511_el = etree.fromstring(resp.content)
        assert open511_el.tag == 'open511'
        open511_validator.validate(open511_el)

        return open511_el
