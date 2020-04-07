import base64
import uuid

import click
from jose import jwt


@click.command()
def main():
    shop_guid = uuid.UUID(click.prompt("Shop GUID: "))
    key = base64.b64decode(click.prompt("Base64 encoded token signing key: "))
    token = jwt.encode(
        dict(
            iss=f"shop:{shop_guid}",
            organization_guid=str(shop_guid),
            groups=["shopkeeper"],
        ),
        key,
        algorithm="HS256",
    )

    print(f"Bearer {token}")


if __name__ == "__main__":
    main()
