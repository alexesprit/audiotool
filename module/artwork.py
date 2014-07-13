import os

__all__ = ['create_artwork', 'is_file_supported', ]


class Artwork:
    def __init__(self, mime, data):
        self.mime = mime
        self.data = data


_MIME_MAP = {
    '.jpg': u'image/jpg',
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


def is_file_supported(filename):
    extension = os.path.splitext(filename)[1]
    return extension in _MIME_MAP
