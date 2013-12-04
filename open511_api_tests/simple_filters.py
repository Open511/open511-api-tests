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
        self.assertEquals(len(default.xpath('events/event')), 6)
        assert len(active.xpath('events/event')) == 6
        archived = self.get_events(status='ARCHIVED')
        assert not archived.xpath('//status[text()="ACTIVE"]')
        assert len(archived.xpath('events/event')) == 13
        all_ = self.get_events(status='ALL')
        assert len(all_.xpath('events/event')) == 19
        assert len(all_.xpath('//status[text()="ACTIVE"]')) == 6
        assert len(all_.xpath('//status[text()="ARCHIVED"]')) == 13
     
    def test_pagination(self):
        first_page = self.get_events(limit=7, status='ALL')
        self.assertEquals(len(first_page.xpath('events/event')), 7)
        first_page_ids = set(first_page.xpath('events/event/id/text()'))

        second_page = self.get_events(url=first_page.xpath('pagination/link[@rel="next"]/@href')[0], limit=7)
        self.assertEquals(len(second_page.xpath('events/event')), 7)
        second_page_ids = set(second_page.xpath('events/event/id/text()'))

        third_page = self.get_events(url=second_page.xpath('pagination/link[@rel="next"]/@href')[0], limit=7)
        self.assertEquals(len(third_page.xpath('events/event')), 5)
        third_page_ids = set(third_page.xpath('events/event/id/text()'))
        self.assertEquals(len(third_page.xpath('pagination/link[@rel="next"]')), 0)

        self.assertEquals(len(first_page_ids.intersection(second_page_ids).intersection(third_page_ids)), 0)

