import os

__all__ = [
    'Artwork', 'create_artwork',
    'is_artwork_supported', 'is_artwork_file',
]


class Artwork(object):
    def __init__(self, mime, data):
        self.mime = mime
        self.data = data

    def __eq__(self, other):
        return self.data == other.data and self.mime == other.mime


_MIME_MAP = {
    '.jpeg': u'image/jpeg',
    '.jpg': u'image/jpeg',
    '.png': u'image/png',
}


def _get_mime(filename):
    extension = os.path.splitext(filename)[1]
    try:
        return _MIME_MAP[extension]
    except KeyError:
        raise RuntimeError


def create_artwork(filename):
    with open(filename, 'rb') as fd:
        data = fd.read()
    mime = _get_mime(filename)
    return Artwork(mime, data)


def is_artwork_file(filename):
    return is_artwork_supported(filename)


def is_artwork_supported(filename):
    extension = os.path.splitext(filename)[1]
    return extension in _MIME_MAP
