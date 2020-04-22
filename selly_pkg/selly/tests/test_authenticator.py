from unittest import TestCase, mock

import responses
from selly.importer import Authenticator
from selly.tests.common import DUMMY_SELLY_URL, API_ID, APP_KEY, HEX_DIGEST
from selly.tests.selly_responses import *


@mock.patch("selly.importer.SELLY_API_URL", DUMMY_SELLY_URL)
class AuthenticatorTests(TestCase):
    def setUp(self) -> None:
        self.authenticator = Authenticator(API_ID, APP_KEY)
        responses.start()
        responses.add(responses.GET, f"{DUMMY_SELLY_URL}?api={API_ID}", json=COIN)
        responses.add(responses.GET, f"{DUMMY_SELLY_URL}?key={HEX_DIGEST}", json=TOKEN)

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_get_coin(self):
        coin = self.authenticator._get_coin()
        self.assertEqual(coin, str(COIN["coin"]))

    def test_get_token_sets_coin_when_coin_not_set(self):
        with mock.patch("selly.importer.Authenticator._get_coin") as mocked_get_coin:
            mocked_get_coin.return_value = str(COIN["coin"])
            self.authenticator.get_token()
            self.assertTrue(mocked_get_coin.called)

    def test_get_token_uses_already_set_coin(self):
        self.authenticator.coin = str(COIN["coin"])
        with mock.patch("selly.importer.Authenticator._get_coin") as mocked_get_coin:
            self.authenticator.get_token()
            self.assertFalse(mocked_get_coin.called)

    def test_get_token(self):
        token = self.authenticator.get_token()
        self.assertEqual(token, TOKEN["success"]["token"])
