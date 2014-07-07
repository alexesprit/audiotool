import os
import unittest

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


class TagWrapperTest(unittest.TestCase):
    def setUp(self):
        self.m4afiles = {
            os.path.join('test', '1.m4a'): {
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            os.path.join('test', '2.m4a'): {
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
        }
        self.mp3files = {
            os.path.join('test', '1.mp3'): {
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            os.path.join('test', '2.mp3'): {
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
        }

    def _test_some_tags(self, files):
        for filename in files:
            tag = TagWrapper(filename)
            test_keys = files[filename]
            for key in test_keys:
                expected = test_keys[key]
                actual = tag[key]
                self.assertEqual(actual, expected)

    def test_m4a_tags(self):
        self._test_some_tags(self.m4afiles)

    def test_mp3_tag(self):
        self._test_some_tags(self.mp3files)


if '__main__' == __name__:
    unittest.main()
