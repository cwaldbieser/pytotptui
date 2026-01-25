from pyzbar.pyzbar import decode
from pyzbar.pyzbar_error import PyZbarError
from PIL import Image


def decode_qr_code(qr_image_path):
    """
    Decode a QR code and return a URL.
    """
    try:
        result = decode(Image.open(qr_image_path))
        url = result[0].data.decode("utf-8")
        return url
    except PyZbarError:
        return None
