import os
import unittest

from tag import get_tags


AUDIO_TEXT_EXAMPLES_DIR = 'audio_examples'


class TagWrapperTest(unittest.TestCase):
    def setUp(self):
        self.m4afiles = {
            self._get_example_path('1.m4a'): {
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            self._get_example_path('2.m4a'): {
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
        }
        self.mp3files = {
            self._get_example_path('1.mp3'): {
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            self._get_example_path('2.mp3'): {
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
        }

    def _get_example_path(self, example_name):
        return os.path.join(AUDIO_TEXT_EXAMPLES_DIR, example_name)

    def _test_some_tags(self, files):
        for filename in files:
            tag = get_tags(filename)
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
