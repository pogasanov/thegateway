import requests

from gateway.models import Image
from utils.io import ResponseStream


def download_image(url, default_filename=None, **kwargs):
    r = requests.head(url, **kwargs)
    sha1 = r.headers.get("Content-Sha1", default_filename)
    mimetype = r.headers["Content-Type"]
    filename = f'{sha1}.{mimetype.rsplit("/")[-1]}'

    stream = ResponseStream(requests.get(url, stream=True, **kwargs).iter_content(64))
    return Image(filename=filename, mimetype=mimetype, data=stream)
