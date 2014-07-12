# coding: utf-8
import argparse
import codecs
import os
import sys
from paths import gen_audio_files, gen_directories

from tag import TagWrapper
from normalize import normalize_path, normalize_string


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
            tag = TagWrapper(filename)
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
        covered = False
        for subitem in os.listdir(item):
            ext = os.path.splitext(subitem)[1]
            if ext in ('.jpg', '.png', '.jpeg'):
                covered = True
        if not covered:
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
            tag = TagWrapper(filename)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='directory', help='Path to scanning')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', dest='genres', action='store_true', help='collect genres')
    group.add_argument('-r', dest='rename', action='store_true', help='rename directories')
    group.add_argument('-t', dest='tags', action='store_true', help='fix ID3 tags')
    group.add_argument('-c', dest='covers', action='store_true', help='search uncovered folders')
    args = parser.parse_args()

    if args.tags:
        fix_audio_tags(args.directory)
    elif args.rename:
        rename_dirs(args.directory)
    elif args.genres:
        collect_genres(args.directory)
    elif args.covers:
        search_uncovered_dirs(args.directory)
    return 0


if '__main__' == __name__:
    sys.exit(main())
