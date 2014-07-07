import os
import re
import unittest


WORDS_TO_REPLACE = (
    'a', 'an', 'the',

    'and', 'or',

    'as', 'at', 'but', 'by',
    'for', 'in', 'of', 'off',
    'on', 'per', 'to', 'up',
    'via', 'yet',

    'am', 'was', 'is', 'are',
)


def _gen_regexp_pattern(word):
    # Don't match: [-.:_] EXPR [(-]
    pattern = '(?<![\-\._:]) %s (?![\(\-])' % word
    return pattern


def normalize_path(path):
    elements = path.split(os.sep)
    for i in xrange(0, len(elements)):
        elements[i] = normalize_string(elements[i])
    return os.sep.join(elements)


def normalize_string(string):
    for word in WORDS_TO_REPLACE:
        pattern = _gen_regexp_pattern(word.capitalize())
        replace = ' %s ' % word
        string = re.sub(pattern, replace, string)
    return string


class StringNormalizationTest(unittest.TestCase):
    def setUp(self):
        self.string_test_map = {
            'Periscope Up': 'Periscope Up',
            'Control The Storm': 'Control the Storm',
            'Build It Up - Tear It Down': 'Build It Up - Tear It Down',
            'Emergency Broadcast :: The End is Near': 'Emergency Broadcast :: The End is Near',
        }
        self.path_test_map = {
            '01 - The One Is The One': '01 - The One is the One',
            '02 - The Rockafeller Skank': '02 - The Rockafeller Skank',
        }

    def test_path_normalization(self):
        for testing, expected in self.path_test_map.iteritems():
            actual = normalize_path(testing)
            self.assertEqual(actual, expected)

    def test_string_normalization(self):
        for testing, expected in self.string_test_map.iteritems():
            actual = normalize_string(testing)
            self.assertEqual(actual, expected)


if '__main__' == __name__:
    unittest.main()
