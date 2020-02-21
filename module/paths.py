import os

from module.tag import is_audio_supported


__all__ = ['gen_audio_files', 'gen_directories', ]


def _gen_files(directory, only_first, check_func):
    for root, dirs, files in os.walk(directory):
        for fn in files:
            if check_func(fn):
                yield os.path.join(root, fn)
                if only_first:
                    break


def gen_audio_files(directory, only_first=False):
    return _gen_files(directory, only_first, is_audio_supported)


def gen_directories(directory, with_files=False):
    for root, dirs, files in os.walk(directory):
        if files or not with_files:
            yield root
