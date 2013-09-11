import os

from open511_api_tests.base import BaseCase

_this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(_this_dir, 'data')

class SimpleFiltersCase(BaseCase):

    @classmethod
    def setUpClass(cls):
        super(SimpleFiltersCase, cls).setUpClass()
        with open(os.path.join(data_dir, 'one.xml')) as f:
          cls.load(f.read())

    def test_smoke(self):
        self.get_events()

    def test_status_filter(self):
        default = self.get_events()
        # import pdb; pdb.set_trace()
        active = self.get_events(status='ACTIVE')
        self.assertEquals(len(default.xpath('event')), 6)
        assert len(active.xpath('event')) == 6
        archived = self.get_events(status='ARCHIVED')
        assert not archived.xpath('//status[text()="ACTIVE"]')
        assert len(archived.xpath('event')) == 13
        all_ = self.get_events(status='ALL')
        assert len(all_.xpath('event')) == 19
        assert len(all_.xpath('//status[text()="ACTIVE"]')) == 6
        assert len(all_.xpath('//status[text()="ARCHIVED"]')) == 13
     

