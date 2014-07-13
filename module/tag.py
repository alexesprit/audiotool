import os

from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4


class _AbstractWrapper:
    def __init__(self):
        pass

    def __getitem__(self, item):
        raise NotImplementedError

    def __setitem__(self, item, value):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class _MP3Wrapper(_AbstractWrapper):
    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = EasyID3(filename)

    def __getitem__(self, item):
        try:
            return self.audio[item][0]
        except KeyError:
            return None

    def __setitem__(self, item, value):
        self.audio[item] = [value]

    def save(self):
        self.audio.save(v1=1, v2_version=3)


class _MP4Wrapper(_AbstractWrapper):
    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = EasyMP4(filename)

    def __getitem__(self, item):
        try:
            return self.audio[item][0]
        except KeyError:
            return None

    def __setitem__(self, item, value):
        self.audio[item] = [value]

    def __repr__(self):
        return self.audio.pprint()

    def save(self):
        self.audio.save()


_WRAPPER_MAP = {
    '.mp3': _MP3Wrapper,
    '.m4a': _MP4Wrapper,
}


def get_tags(filename):
    extension = os.path.splitext(filename)[1]
    try:
        return _WRAPPER_MAP[extension](filename)
    except KeyError:
        raise RuntimeError


def is_audio_supported(filename):
    extension = os.path.splitext(filename)[1]
    return extension in _WRAPPER_MAP
