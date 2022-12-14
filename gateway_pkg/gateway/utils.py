import requests

from .io import ResponseStream
from .models import Image


def download_image(url, default_filename=None, **kwargs):
    response = requests.head(url, **kwargs)
    sha1 = response.headers.get("Content-Sha1", default_filename)
    mimetype = response.headers["Content-Type"]
    filename = f'{sha1}.{mimetype.rsplit("/")[-1]}'

    stream = ResponseStream(requests.get(url, stream=True, **kwargs).iter_content(64))
    return Image(filename=filename, mimetype=mimetype, data=stream)
