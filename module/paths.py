import os
import sys

from module.tag import TagWrapper


def decode_path(function):
    def wrapper2x(*args, **kwargs):
        for item in function(*args, **kwargs):
            yield item.decode(sys.getfilesystemencoding())

    def wrapper3x(*args, **kwargs):
        for item in function(*args, **kwargs):
            yield item

    if sys.version_info > (3, ):
        return wrapper3x
    else:
        return wrapper2x


@decode_path
def gen_audio_files(directory, only_first=False):
    for fp in _gen_files(directory, only_first, TagWrapper.is_supported):
        yield fp

@decode_path
def gen_directories(directory, with_files=False):
    for root, dirs, files in os.walk(directory):
        if files or not with_files:
            yield root


def _gen_files(directory, only_first, check_func):
    for root, dirs, files in os.walk(directory):
        for fn in files:
            if check_func(fn):
                yield os.path.join(root, fn)
                if only_first:
                    break
