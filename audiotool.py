# coding: utf-8
import argparse
import codecs
import os
import sys
from module.artwork import is_artwork_file, create_artwork

from module.normalize import normalize_path, normalize_string

from module.paths import gen_audio_files, gen_directories
from module.tag import get_tags, is_audio_file


GENRE_OUT_FILENAME = 'genres.txt'


def keyboard_interrupt(function):
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except KeyboardInterrupt:
            print(u'Cancelled')

    return wrapper


def print_scanning(function):
    def wrapper(directory):
        print(u'Scanning %s' % os.path.abspath(directory))
        function(directory)

    return wrapper


@keyboard_interrupt
@print_scanning
def fix_audio_tags(directory):
    for filename in gen_audio_files(directory):
        try:
            tag = get_tags(filename)
        except IOError:
            print(u'[fix_audio_tags] error: set tag for %s' % filename)
            continue

        old_artist = tag['artist']
        old_album = tag['album']
        old_title = tag['title']

        new_artist = normalize_string(old_artist)
        new_album = normalize_string(old_album)
        new_title = normalize_string(old_title)

        changed = False
        if old_artist != new_artist:
            tag['artist'] = new_artist
            changed = True
        if old_album != new_album:
            tag['album'] = new_album
            changed = True
        if old_title != new_title:
            tag['title'] = new_title
            changed = True
        if changed:
            tag.save()
            print(u'[!] file updated: %s' % filename)
        new_filename = normalize_path(filename)
        if filename != new_filename:
            os.rename(filename, new_filename)
            print(u'[!] file renamed: %s' % filename)


@keyboard_interrupt
@print_scanning
def rename_dirs(directory):
    renamed_dirs = []
    for item in gen_directories(directory, with_files=False):
        old_path = item
        new_path = normalize_path(old_path)
        if old_path != new_path:
            os.rename(old_path, new_path)
            renamed_dirs.append(old_path)
    if renamed_dirs:
        for path in renamed_dirs:
            print(u'folder renamed: %s' % path)
    else:
        print(u'Nothing is renamed')


@keyboard_interrupt
@print_scanning
def search_uncovered_dirs(directory):
    uncovered_dirs = []
    for item in gen_directories(directory, with_files=True):
        for subitem in os.listdir(item):
            ext = os.path.splitext(subitem)[1]
            if ext in ('.jpg', '.png', '.jpeg'):
                break
        else:
            uncovered_dirs.append(item)
    if uncovered_dirs:
        for path in uncovered_dirs:
            print(u'Uncovered: %s' % path)
    else:
        print(u'All directories have covers')


@keyboard_interrupt
@print_scanning
def collect_genres(directory):
    genres = {}
    for filename in gen_audio_files(directory, only_first=True):
        try:
            tag = get_tags(filename)
        except IOError:
            print(u'[collect_genres] error: get tag from %s' % filename)
            continue

        genre = tag['genre']
        if genre:
            if genre not in genres:
                genres[genre] = []
            basedir = os.path.dirname(filename)
            genres[genre].append(basedir)

    with codecs.open(GENRE_OUT_FILENAME, 'w', 'utf-8') as fd:
        for genre in genres:
            fd.write(genre + ':\n')
            for item in genres[genre]:
                fd.write(item + '\n')
            fd.write('\n')
    filepath = os.path.join(os.getcwd(), 'genres.txt')
    print(u'genre info written to %s' % filepath)


@keyboard_interrupt
@print_scanning
def attach_artworks(directory):
    for item in gen_directories(directory, with_files=True):
        dir_items = os.listdir(item)
        for subitem in dir_items:
            subitem_path = os.path.join(item, subitem)
            if is_artwork_file(subitem_path):
                artwork_filename = subitem_path
                break
        else:
            continue
        artwork = create_artwork(artwork_filename)
        for subitem in dir_items:
            subitem_path = os.path.join(item, subitem)
            if is_audio_file(subitem_path):
                tag = get_tags(subitem_path)
                tag['artwork'] = artwork
                tag.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='directory', help='Path to scanning')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', dest='artwork', action='store_true', help='attach album artwork to audio files')
    group.add_argument('-g', dest='genres', action='store_true', help='collect genres')
    group.add_argument('-r', dest='rename', action='store_true', help='normalize directories names')
    group.add_argument('-t', dest='tags', action='store_true', help='normalize audio tags')
    group.add_argument('-u', dest='uncovered', action='store_true', help='search folders without album artwork')
    args = parser.parse_args()

    if args.tags:
        fix_audio_tags(args.directory)
    elif args.rename:
        rename_dirs(args.directory)
    elif args.genres:
        collect_genres(args.directory)
    elif args.uncovered:
        search_uncovered_dirs(args.directory)
    elif args.artwork:
        attach_artworks(args.directory)
    return 0


if '__main__' == __name__:
    sys.exit(main())
