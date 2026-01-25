from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.pyzbar_error import PyZbarError


def decode_qr_code(qr_image_path):
    """
    Decode a QR code and return a URL.
    """
    try:
        result = decode(Image.open(qr_image_path))
        url = result[0].data.decode("utf-8")
    except PyZbarError:
        return None
    p = urlparse(url)
    qs = parse_qsl(p.query)
    qs = dict(qs)
    name = qs.get("name", "")
    issuer = qs.get("issuer", p.path[1:])
    if name == "" and "name" in qs:
        del qs["name"]
    else:
        qs["name"] = name
    if "issuer" in qs:
        del qs["issuer"]
    query = urlencode(qs)
    path = f"/{issuer}"
    url = urlunparse((p.scheme, p.netloc, path, p.params, query, p.fragment))
    return url
