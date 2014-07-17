from distutils.dir_util import copy_tree, remove_tree
import os
import tempfile
import unittest

from artwork import create_artwork
from tag import get_tags, TagValueError


AUDIO_EXAMPLES_DIR = 'audio_examples'
COVER_EXAMPLE_PATH = os.path.join(AUDIO_EXAMPLES_DIR, 'cover.jpg')


class TagWrapperTest(unittest.TestCase):
    def setUp(self):
        self.formats = ('flac', 'm4a', 'mp3', 'ogg')
        self.read_test_data_map = {
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
                'artwork': create_artwork(COVER_EXAMPLE_PATH),
                'artist': 'Test Artist',
                'album': 'Test Album',
                'title': 'Test Title',
            },
        }
        self.write_test_data_map = {
            '1': {
                'artwork': create_artwork(COVER_EXAMPLE_PATH),
                'artist': 'Write Test Artist',
                'album': 'Write Test Album',
                'title': 'Write Test Title',
            },
        }
        self.write_wrong_data_map = {
            '1': ('artwork', 'artist', 'album', 'title', 'genre')
        }

    def test_getting_tags(self):
        test_data = self._gen_test_data(AUDIO_EXAMPLES_DIR, self.read_test_data_map)
        self._test_read_tags(test_data)

    def test_setting_tags(self):
        temp_dir = tempfile.mkdtemp()
        copy_tree(AUDIO_EXAMPLES_DIR, temp_dir)
        test_data = self._gen_test_data(temp_dir, self.write_test_data_map)
        self._test_write_tags(test_data)
        self._test_read_tags(test_data)
        remove_tree(temp_dir)

    def test_writing_wrong_data(self):
        test_data = self._gen_test_data(AUDIO_EXAMPLES_DIR, self.write_wrong_data_map)
        self._test_writing_wrong_data(test_data)

    def _gen_test_data(self, directory, data_map):
        for fn in data_map:
            for ext in self.formats:
                full_fn = '{0:s}.{1:s}'.format(fn, ext)
                fp = os.path.join(directory, full_fn)
                yield get_tags(fp), data_map[fn]

    def _test_read_tags(self, test_data):
        for tag, data in test_data:
            for key in data:
                expected = data[key]
                actual = getattr(tag, key)
                self.assertEqual(actual, expected)

    def _test_write_tags(self, test_data):
        for tag, data in test_data:
            for key in data:
                value = data[key]
                setattr(tag, key, value)
            tag.save()

    def _test_writing_wrong_data(self, test_data):
        for tag, data in test_data:
            for key in data:
                try:
                    setattr(tag, key, self)
                    self.fail()
                except TagValueError:
                    pass


if '__main__' == __name__:
    unittest.main()
