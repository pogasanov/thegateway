from unittest import TestCase

from prestashop.src.Gateway import Gateway


class GatewayTest(TestCase):
    def test_can_build_token(self):
        EXPECTED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzaG9wOmE1NDdkZTE4LTdhMWQtNDUwYi1hNTdiLWJiZjdmMTc3ZGI4NCIsIm9yZ2FuaXphdGlvbl9ndWlkIjoiYTU0N2RlMTgtN2ExZC00NTBiLWE1N2ItYmJmN2YxNzdkYjg0IiwiZ3JvdXBzIjpbInNob3BrZWVwZXIiXX0.qtkzVdLOEpG2KrLqYHGbHyNTCoNX_r8-_0krBXCMUMo'
        gateway = Gateway()
        self.assertEqual(gateway.token, EXPECTED_TOKEN)
