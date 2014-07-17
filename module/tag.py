from base64 import b64decode, b64encode
import os

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, Frames, ID3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis

from artwork import Artwork


__all__ = ['get_tags', 'is_audio_file', 'is_audio_supported', ]


class TagValueError(ValueError):
    def __init__(self, value):
        message = u'Unknown value type: {0}'.format(value.__class__.__name__)
        ValueError.__init__(self, message)


class TagError(AttributeError):
    def __init__(self, tag, attr):
        message = u"'{0}' object has no attribute '{1}'".format(tag.__class__.__name__, attr)
        AttributeError.__init__(self, message)


class _AbstractWrapper(object):
    def __init__(self):
        pass

    def save(self):
        raise NotImplementedError


class _OggVorbisWrapper(_AbstractWrapper):
    TAG_MAP = {
        'artwork': 'metadata_block_picture',
        'artist': 'artist', 'album': 'album',
        'title': 'title', 'genre': 'genre',
    }
    VALID_TAG_KEYS = ('artwork', 'artist', 'album', 'title', 'genre', )

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = OggVorbis(filename)

    def __getattr__(self, attr):
        if attr in self.VALID_TAG_KEYS:
            if attr == 'artwork':
                try:
                    raw_artwork_data = b64decode(self.audio['metadata_block_picture'][0])
                    picture = Picture(raw_artwork_data)
                    return Artwork(picture.mime, picture.data)
                except KeyError:
                    return None
            else:
                try:
                    return self.audio[attr][0]
                except KeyError:
                    return None
        raise TagError(self, attr)

    def __setattr__(self, attr, value):
        if attr in self.VALID_TAG_KEYS:
            if isinstance(value, Artwork):
                picture = Picture()
                picture.type = 3
                picture.mime = value.mime
                picture.data = value.data
                self.audio['metadata_block_picture'] = [b64encode(picture.write())]
            elif isinstance(value, basestring):
                self.audio[attr] = [value]
            else:
                raise TagValueError(value)
        else:
            object.__setattr__(self, attr, value)

    def __repr__(self):
        return repr(self.audio)

    def save(self):
        self.audio.save()


class _FLACWrapper(_AbstractWrapper):
    VALID_TAG_KEYS = ('artwork', 'artist', 'album', 'title', 'genre', )

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = FLAC(filename)

    def __getattr__(self, attr):
        if attr in self.VALID_TAG_KEYS:
            if attr == 'artwork':
                if self.audio.pictures:
                    picture = self.audio.pictures[0]
                    return Artwork(picture.mime, picture.data)
                else:
                    return None
            else:
                try:
                    return self.audio[attr][0]
                except KeyError:
                    return None
        raise TagError(self, attr)

    def __setattr__(self, attr, value):
        if attr in self.VALID_TAG_KEYS:
            if isinstance(value, Artwork):
                picture = Picture()
                picture.type = 3
                picture.mime = value.mime
                picture.data = value.data
                self.audio.clear_pictures()
                self.audio.add_picture(picture)
            elif isinstance(value, basestring):
                self.audio[attr] = [value]
            else:
                raise TagValueError(value)
        else:
            object.__setattr__(self, attr, value)

    def __repr__(self):
        return repr(self.audio)

    def save(self):
        self.audio.save()


class _MP3Wrapper(_AbstractWrapper):
    TAG_MAP = {
        'artwork': 'APIC:',
        'artist': 'TPE1', 'album': 'TALB',
        'title': 'TIT2', 'genre': 'TCON',
    }

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = ID3(filename)

    def __getattr__(self, attr):
        if attr in self.TAG_MAP:
            frame_id = _MP3Wrapper.TAG_MAP[attr]
            try:
                frame = self.audio[frame_id]
                if 'artwork' == attr:
                    return Artwork(frame.mime, frame.data)
                else:
                    return frame.text[0]
            except KeyError:
                return None
        raise TagError(self, attr)

    def __setattr__(self, attr, value):
        if attr in self.TAG_MAP:
            frame_id = self.TAG_MAP[attr]
            frame = self.audio.get(frame_id, None)
            if isinstance(value, Artwork):
                if not frame:
                    frame = APIC(encoding=3, type=3)
                    self.audio.add(frame)
                frame.data = value.data
                frame.mime = value.mime
            elif isinstance(value, basestring):
                if not frame:
                    frame = Frames[frame_id](encoding=3)
                    self.audio.add(frame)
                frame.text = [value]
            else:
                raise TagValueError(value)
        else:
            object.__setattr__(self, attr, value)

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
    COVER_MIME_MAP = {
        'image/jpeg': MP4Cover.FORMAT_JPEG,
        'image/png': MP4Cover.FORMAT_PNG,
    }
    COVER_FORMAT_MAP = {
        MP4Cover.FORMAT_JPEG: 'image/jpeg',
        MP4Cover.FORMAT_PNG: 'image/png',
    }

    def __init__(self, filename):
        _AbstractWrapper.__init__(self)
        self.audio = MP4(filename)

    def __getattr__(self, attr):
        if attr in self.TAG_MAP:
            tag_id = _MP4Wrapper.TAG_MAP[attr]
            try:
                tag = self.audio[tag_id][0]
                if 'artwork' == attr:
                    mime = _MP4Wrapper._get_mime_by_format(tag.imageformat)
                    return Artwork(mime, tag[:])
                else:
                    return tag
            except KeyError:
                return None
        raise TagError(self, attr)

    def __setattr__(self, attr, value):
        if attr in self.TAG_MAP:
            tag_id = _MP4Wrapper.TAG_MAP[attr]
            if isinstance(value, Artwork):
                imageformat = _MP4Wrapper._get_format_by_mime(value.mime)
                mp4_cover = MP4Cover(value.data, imageformat=imageformat)
                self.audio[tag_id] = [mp4_cover]
            elif isinstance(value, basestring):
                self.audio[tag_id] = [value]
            else:
                raise TagValueError(value)
        else:
            object.__setattr__(self, attr, value)

    def __repr__(self):
        return repr(self.audio)

    def save(self):
        self.audio.save()

    @staticmethod
    def _get_format_by_mime(mime):
        try:
            return _MP4Wrapper.COVER_MIME_MAP[mime]
        except:
            raise ValueError('Unknown image MIME: %s' % mime)

    @staticmethod
    def _get_mime_by_format(imageformat):
        try:
            return _MP4Wrapper.COVER_FORMAT_MAP[imageformat]
        except:
            raise ValueError('Unknown image format: %s' % imageformat)

_WRAPPER_MAP = {
    '.flac': _FLACWrapper, '.ogg': _OggVorbisWrapper,
    '.mp3': _MP3Wrapper, '.m4a': _MP4Wrapper,
}


def get_tags(filename):
    extension = os.path.splitext(filename)[1]
    try:
        return _WRAPPER_MAP[extension](filename)
    except KeyError:
        raise RuntimeError('Unknown file format: %s' % extension)


def is_audio_file(filename):
    return is_audio_supported(filename)


def is_audio_supported(filename):
    extension = os.path.splitext(filename)[1]
    return extension in _WRAPPER_MAP
