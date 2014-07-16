import os
import unittest

from tag import get_tags


AUDIO_EXAMPLES_DIR = 'audio_examples'
COVER_EXAMPLE_PATH = os.path.join(AUDIO_EXAMPLES_DIR, 'cover.jpg')


class TagWrapperTest(unittest.TestCase):
    def setUp(self):
        self.test_files = {
            # FLAC
            self._get_example_path('1.flac'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            self._get_example_path('2.flac'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
            self._get_example_path('3.flac'): {
                'artwork': self._get_cover_data(),
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            # MP3
            self._get_example_path('1.mp3'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            self._get_example_path('2.mp3'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
            self._get_example_path('3.mp3'): {
                'artwork': self._get_cover_data(),
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            # M4A
            self._get_example_path('1.m4a'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            self._get_example_path('2.m4a'): {
                'artwork': None,
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
            self._get_example_path('3.m4a'): {
                'artwork': self._get_cover_data(),
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
        }

    def _get_example_path(self, example_name):
        return os.path.join(AUDIO_EXAMPLES_DIR, example_name)

    def _get_cover_data(self):
        with open(COVER_EXAMPLE_PATH, 'rb') as fd:
            return fd.read()

    def test_getting_tags(self):
        for filename in self.test_files:
            tag = get_tags(filename)
            test_keys = self.test_files[filename]
            for key in test_keys:
                expected = test_keys[key]
                actual = getattr(tag, key)
                self.assertEqual(actual, expected)

    def test_setting_tags(self):
        for filename in self.test_files:
            tag = get_tags(filename)
            for key in ('artist', 'album', 'title'):
                value = 'key_{0:s}'.format(key)
                setattr(tag, key, value)
                self.assertEqual(getattr(tag, key), value)


if '__main__' == __name__:
    unittest.main()
