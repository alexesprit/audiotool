import unittest
from normalize import normalize_path, normalize_string


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
