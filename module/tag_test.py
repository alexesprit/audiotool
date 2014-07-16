import os
import unittest

from tag import get_tags


AUDIO_EXAMPLES_DIR = 'audio_examples'
COVER_EXAMPLE_PATH = os.path.join(AUDIO_EXAMPLES_DIR, 'cover.jpg')


class TagWrapperTest(unittest.TestCase):
    def setUp(self):
        self.test_files = {
            '1': {
                'artwork': None,
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
            '2': {
                'artwork': None,
                'artist': 'Test Artist',
                'album': None,
                'title': 'Test Title',
            },
            '3': {
                'artwork': self._get_cover_data(),
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
        }
        self.formats = ('flac', 'm4a', 'mp3', 'ogg')

    def _get_example_path(self, example_name):
        return os.path.join(AUDIO_EXAMPLES_DIR, example_name)

    def _get_cover_data(self):
        with open(COVER_EXAMPLE_PATH, 'rb') as fd:
            return fd.read()

    def _gen_test_data(self):
        for filename in self.test_files:
            for format in self.formats:
                full_filename = '{0:s}.{1:s}'.format(filename, format)
                filepath = os.path.join(AUDIO_EXAMPLES_DIR, full_filename)
                yield get_tags(filepath), self.test_files[filename]

    def test_getting_tags(self):
        for tag, data in self._gen_test_data():
            for key in data:
                expected = data[key]
                actual = getattr(tag, key)
                self.assertEqual(actual, expected)

    def test_setting_tags(self):
        for tag, data in self._gen_test_data():
            for key in ('artist', 'album', 'title'):
                value = 'key_{0:s}'.format(key)
                setattr(tag, key, value)
                self.assertEqual(getattr(tag, key), value)


if '__main__' == __name__:
    unittest.main()
