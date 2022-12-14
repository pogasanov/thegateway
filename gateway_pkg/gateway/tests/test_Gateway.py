import io
from decimal import Decimal
from unittest import TestCase, mock

import gateway
import responses

from .gateway_responses import GATEWAY_PRODUCT, GATEWAY_TAG


class GatewayTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = "http://123.456.789.0"
        cls.SHOP_ID = "a547de18-7a1d-450b-a57b-bbf7f177db84"
        cls.SECRET = "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys="
        cls.IMAGE_URL_PREFIX = "test_"
        cls.gateway = gateway.Gateway(cls.BASE_URL, cls.SHOP_ID, cls.SECRET, cls.IMAGE_URL_PREFIX)

    def setUp(self):
        responses.start()
        responses.add(
            responses.POST, f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/", json=GATEWAY_PRODUCT, status=200,
        )
        responses.add(
            responses.POST, f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products", json={}, status=200,
        )
        responses.add(
            responses.POST, f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/", json=GATEWAY_TAG, status=201,
        )
        responses.add(responses.GET, f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/", json=[], status=200,),
        responses.add(
            responses.POST,
            f"{self.BASE_URL}/uploads/",
            json={"url": "http://dummy.com/", "fields": {"key": "abc"}},
            status=200,
        )
        responses.add(responses.POST, "http://dummy.com", json={}, status=200)

    def tearDown(self):
        responses.stop()
        responses.reset()

    def test_can_build_token(self):
        expected_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzaG9wOmE1NDdkZTE4LTdhMWQtNDUwYi1hNTdiLWJiZjdmMTc3ZGI4NCIsIm9yZ2FuaXphdGlvbl9ndWlkIjoiYTU0N2RlMTgtN2ExZC00NTBiLWE1N2ItYmJmN2YxNzdkYjg0IiwiZ3JvdXBzIjpbInNob3BrZWVwZXIiXX0.qtkzVdLOEpG2KrLqYHGbHyNTCoNX_r8-_0krBXCMUMo"
        token = self.gateway._build_token(self.SECRET)
        self.assertEqual(token, expected_token)

    def test_can_create_product(self):
        product = gateway.Product(name="abc", price=Decimal("12.0"), vat_percent=23)
        self.gateway.create_products([product])

    def test_can_upload_image(self):
        new_url = self.gateway.upload_image(
            gateway.Image(filename="abc.jpeg", mimetype="image/jpeg", data=gateway.ResponseStream(io.BytesIO(b"abc")),)
        )
        self.assertEqual(new_url, "http://dummy.com/abc")

    @mock.patch("gateway.gateway.Gateway._get_tag", return_value=None)
    def test_create_tag_which_doesnt_exist(self, mock_get_tag):
        tag = self.gateway.create_tag("test")
        assert mock_get_tag.called
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/"
        assert tag == GATEWAY_TAG["guid"]

    @mock.patch("gateway.gateway.Gateway._get_tag", return_value=GATEWAY_TAG)
    def test_create_tag_which_exists(self, mock_get_tag):
        tag = self.gateway.create_tag("test")
        assert mock_get_tag.called
        assert len(responses.calls) == 0
        assert tag == GATEWAY_TAG["guid"]

    def test_get_tag_guid_from_conflict_message(self):
        conflict_message = "Tag (403b62c1-5370-53ad-b71d-8ed1916c94f7) already exists"
        guid = self.gateway._get_tag_guid_from_conflict_message(conflict_message)
        assert guid == "403b62c1-5370-53ad-b71d-8ed1916c94f7"

    def test_create_tag_with_409_response(self):
        with responses.RequestsMock() as responses_mock:
            expected_tag_guid = "403b62c1-5370-53ad-b71d-8ed1916c94f7"
            responses_mock.add(responses.GET, f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/", json=[], status=200,),
            responses_mock.add(
                responses.POST,
                f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/",
                json={"code": 409, "error": "409 Conflict", "message": f'"Tag ({expected_tag_guid}) already exists"'},
                status=409,
            )
            tag = self.gateway.create_tag("test")
            assert responses_mock.calls[1].request.url == f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/"
            assert responses_mock.calls[1].response.status_code == 409
            assert tag == expected_tag_guid

    def test_escape_non_ascii_characters_in_url(self):
        non_ascii_url = "http://example.com/image/sk??plikowana_nazwa_zdj??cia.jpg"
        fixed_path = gateway.Gateway._escape_non_ascii_characters_in_url(non_ascii_url)
        self.assertEqual("http://example.com/image/sk%C4%85plikowana_nazwa_zdj%C4%99cia.jpg", fixed_path)
        self.assertTrue(fixed_path.isascii())
