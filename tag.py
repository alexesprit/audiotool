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

    def save(self):
        self.audio.save()


class TagWrapper:
    WRAPPER_MAP = {
        '.mp3': _MP3Wrapper,
        '.m4a': _MP4Wrapper,
    }

    @staticmethod
    def is_supported(filename):
        extension = os.path.splitext(filename)[1]
        return extension in TagWrapper.WRAPPER_MAP

    def __init__(self, filename):
        extension = os.path.splitext(filename)[1]
        try:
            tag_type = TagWrapper.WRAPPER_MAP[extension]

        except KeyError:
            raise RuntimeError

        self.audio = tag_type(filename)
        self.__getitem__ = self.audio.__getitem__
        self.__setitem__ = self.audio.__setitem__
        self.save = self.audio.save


