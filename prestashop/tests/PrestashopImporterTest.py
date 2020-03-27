from unittest import TestCase

from prestashop.PrestashopImporter import PrestashopImporter


class PrestashopImporterTest(TestCase):
    def test_can_init(self):
        PrestashopImporter()
