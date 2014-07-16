import os

from mutagen.id3 import Frames, APIC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover

from artwork import Artwork


__all__ = ['get_tags', 'is_audio_file', 'is_audio_supported', ]


class _AbstractWrapper(object):
    def __init__(self):
        pass

    def _set_tag(self, tag, value):
        raise NotImplementedError


class _MP3Wrapper(_AbstractWrapper):
    TAG_MAP = {
        'artwork': 'APIC:',
        'artist': 'TPE1', 'album': 'TALB',
        'title': 'TIT2', 'genre': 'TCON',
    }

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = MP3(filename)

    def __getattr__(self, attr):
        if attr in self.TAG_MAP:
            frame_id = _MP3Wrapper.TAG_MAP[attr]
            try:
                if 'artwork' == attr:
                    return self.audio[frame_id].data
                else:
                    return self.audio[frame_id].text[0]
            except KeyError:
                return None
        raise AttributeError

    def __setattr__(self, attr, value):
        if attr in self.TAG_MAP:
            frame_id = self.TAG_MAP[attr]
            frame = self.audio.get(frame_id, None)
            if isinstance(value, Artwork):
                if not frame:
                    frame = APIC(encoding=3, type=3)
                    self.audio.tags.add(frame)
                frame.data = value.data
                frame.mime = value.mime
            elif isinstance(value, basestring):
                if not frame:
                    frame = Frames[frame_id](encoding = 3)
                    self.audio.tags.add(frame)
                frame.text = [value]
            else:
                raise ValueError('Unknown item type')
        else:
            self.__dict__[attr] = value

    def __repr__(self):
        return repr(self.audio)

    def save(self):
        self.audio.save(v1=1, v2_version=3)


class _MP4Wrapper(_AbstractWrapper):
    TAG_MAP = {
        'artwork': 'covr',
        'artist': '\xa9ART', 'album': '\xa9alb',
        'title': '\xa9nam', 'genre': '\xa9gen',
    }
    COVER_FOFMAT_MAP = {
        'image/jpeg': MP4Cover.FORMAT_JPEG,
        'image/png': MP4Cover.FORMAT_PNG,
    }

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = MP4(filename)

    def __getattr__(self, attr):
        if attr in self.TAG_MAP:
            tag_id = _MP4Wrapper.TAG_MAP[attr]
            try:
                return self.audio[tag_id][0]
            except KeyError:
                return None
        raise AttributeError

    def __setattr__(self, attr, value):
        if attr in self.TAG_MAP:
            tag_id = _MP4Wrapper.TAG_MAP[attr]
            if isinstance(value, Artwork):
                try:
                    imageformat = _MP4Wrapper.COVER_FOFMAT_MAP[value.mime]
                except:
                    raise ValueError('Unknown image format: %s' % value.mime)
                mp4_cover = MP4Cover(value.data, imageformat=imageformat)
                self.audio[tag_id] = [mp4_cover]
            elif isinstance(value, basestring):
                self.audio[tag_id] = [value]
            else:
                raise ValueError('Unknown item type')
        else:
            self.__dict__[attr] = value

    def __repr__(self):
        return repr(self.audio)

    def save(self):
        self.audio.save()


_WRAPPER_MAP = {
    '.mp3': _MP3Wrapper,
    '.m4a': _MP4Wrapper,
}


def get_tags(filename):
    extension = os.path.splitext(filename)[1]
    try:
        return _WRAPPER_MAP[extension](filename)
    except KeyError:
        raise RuntimeError


def is_audio_file(filename):
    return is_audio_supported(filename)


def is_audio_supported(filename):
    extension = os.path.splitext(filename)[1]
    return extension in _WRAPPER_MAP
