import re


__all__ = ['normalize_path', 'normalize_string', ]


_WORDS_TO_REPLACE = (
    'a', 'an', 'the',

    'and', 'or',

    'as', 'at', 'but', 'by',
    'for', 'in', 'of', 'off',
    'on', 'per', 'to', 'up',
    'via', 'yet',

    'am', 'was', 'is', 'are',
)


def _gen_regexp_pattern(word):
    # Don't match: [-.:_&] EXPR [(-]
    pattern = '(?<![\-\.:_&]) %s (?![\(\-])' % word
    return pattern


# noinspection PyArgumentList
def normalize_path(path):
    return normalize_string(path)


def normalize_string(string):
    if string:
        for word in _WORDS_TO_REPLACE:
            pattern = _gen_regexp_pattern(word.capitalize())
            replace = ' %s ' % word
            string = re.sub(pattern, replace, string)
    return string
