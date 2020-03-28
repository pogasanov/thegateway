import base64
import os
import uuid

from jose import jwt


class Gateway:
    def __init__(self):
        self.BASE_URL = os.environ.get('GATEWAY_BASE_URL', 'https://sma.dev.gwapi.eu/')
        self.SHOP_ID = os.environ.get('GATEWAY_SHOP_ID', 'a547de18-7a1d-450b-a57b-bbf7f177db84')
        self.SECRET = os.environ.get('GATEWAY_SECRET', 'OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=')

        self.token = self._build_token()

    def _build_token(self):
        shop_guid = uuid.UUID(self.SHOP_ID)
        key = base64.b64decode(self.SECRET)
        return jwt.encode(
            dict(iss=f"shop:{shop_guid}",
                 organization_guid=str(shop_guid),
                 groups=['shopkeeper']
                 ), key, algorithm="HS256")
