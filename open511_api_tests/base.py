import os
from unittest import TestCase
from urlparse import urljoin

from lxml import etree, isoschematron
import requests

API_URL = None
TEST_ENDPOINT_URL = None
USE_DJANGO_TEST_CLIENT = False
EVENTS_URL = None

DjangoTestClient = None

NSMAP = {
    'gml': 'http://www.opengis.net/gml',
}

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
RELAXNG_SCHEMA = etree.RelaxNG(etree.parse(os.path.join(CURRENT_DIR, 'open511.rng')))
SCHEMATRON_DOC = isoschematron.Schematron(etree.parse(os.path.join(CURRENT_DIR, 'open511.schematron')))

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
    event_service = discovery.xpath('services/service[service_type/text()="EVENTS"]')[0]
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

    def get(self, url, params={}, headers={}):
        if USE_DJANGO_TEST_CLIENT:
            cgi_headers = dict(
                ('HTTP_' + key.upper().replace('-', '_'), value)
                for key, value in headers.items()
            )
            return DjangoTestClient().get(url, params, **cgi_headers)
        else:
            return requests.get(url, params=params, headers=headers)

    def get_events(self, **kwargs):
        params = {
            'jurisdiction': 'test.open511.org'
        }
        headers = {
            'Accept': 'application/xml'
        }
        headers.update(kwargs.pop('headers', {}))
        params.update(kwargs)
        resp = self.get(EVENTS_URL, params=params, headers=headers)
        assert resp.status_code == 200
        open511_el = etree.fromstring(resp.content)
        assert open511_el.tag == 'open511'
        for schema in RELAXNG_SCHEMA, SCHEMATRON_DOC:
            schema.assertValid(open511_el)

        return open511_el
