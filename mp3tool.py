# coding: utf-8
import argparse
import glob
import os
import sys

import terminal
from tag import TagWrapper


WORDS_TO_REPLACE = (
    'a', 'an', 'the',

    'and', 'or',

    'as', 'at', 'but', 'by',
    'for', 'in', 'of', 'off',
    'on', 'per', 'to', 'up',
    'via', 'yet',

    'am', 'was', 'is', 'are',
)


def keyboard_interrupt(function):
    def wrapper(*args):
        try:
            function(*args)
        except KeyboardInterrupt:
            println('Cancelled')
    return wrapper


def println(output):
    window_width = terminal.get_terminal_size()[0]
    if len(output) >= window_width:
        output = '%s…' % output[0:window_width - 1]
    output = unicode(output, 'cp1251')
    try:
        if os.name == 'nt':
            output = output.encode('cp866')
        print output
    except UnicodeEncodeError:
        pass


def gen_directories(directory, alldirs):
    for root, dirs, files in os.walk(directory):
        if not files and not alldirs:
            continue
        println('[!] Scanning: %s' % root)
        yield root


def gen_mp3_files(directory):
    def is_mp3(path):
        return os.path.splitext(path)[1] == '.mp3'

    for root, dirs, files in os.walk(directory):
        println('[!] Scanning %s' % root)
        for f in files:
            if is_mp3(f):
                yield os.path.join(root, f)


def normalize_path(path):
    elements = path.split(os.sep)
    for i in xrange(0, len(elements)):
        elements[i] = normalize_string(elements[i])
    return os.sep.join(elements)


def normalize_string(string):
    if not string:
        return None
    matches = (
        ': %s', '- %s', '_ %s', '%s (', '. %s'
    )
    for word in WORDS_TO_REPLACE:
        old_word = word.capitalize()
        old_repl = ' %s ' % old_word
        if string.count(old_repl):
            skip = False
            for m in matches:
                if string.count(m % old_word):
                    skip = True
                    break
            if not skip:
                new_repl = ' %s ' % word
                string = string.replace(old_repl, new_repl)
    return string


@keyboard_interrupt
def fix_audio_tags(directory):
    for filename in gen_mp3_files(directory):
        try:
            tag = TagWrapper(filename)
        except IOError:
            println('[search_mp3] error: set tag for %s' % filename)
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
            println('[!] file updated: %s' % filename)
        new_filename = normalize_path(filename)
        if filename != new_filename:
            os.rename(filename, new_filename)
            println('[!] file renamed: %s' % filename)


@keyboard_interrupt
def rename_dirs(directory):
    renamed_dirs = []
    for item in gen_directories(directory, True):
        old_path = item
        new_path = normalize_path(old_path)
        if old_path != new_path:
            os.rename(old_path, new_path)
            renamed_dirs.append(old_path)
    println('')
    if renamed_dirs:
        for path in renamed_dirs:
            println('[!] folder renamed: %s' % path)
    else:
        println('[!] Nothing is renamed')


@keyboard_interrupt
def search_uncovered_dirs(directory):
    uncovered_dirs = []
    for item in gen_directories(directory, False):
        covered = False
        for subitem in os.listdir(item):
            ext = os.path.splitext(subitem)[1]
            if ext in ('.jpg', '.png', '.jpeg'):
                covered = True
        if not covered:
            uncovered_dirs.append(item)
    println('')
    if uncovered_dirs:
        for path in uncovered_dirs:
            println('[!] Uncovered: %s' % path)
    else:
        println('[!] All directories have covers')


@keyboard_interrupt
def collect_genres(directory):
    genres = {}
    for item in gen_directories(directory, False):
        mp3s = glob.glob(os.path.join(item, '*.mp3'))
        if mp3s:
            filename = mp3s[0]
            try:
                tag = TagWrapper(filename)
            except IOError:
                println('[search_genres] error: get tag from %s' % filename)
                continue

            genre = tag['genre']
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(item)
    out = open('genres.txt', 'w')
    for genre in genres:
        out.write(genre + ':\n')
        for item in genres[genre]:
            out.write(item + '\n')
        out.write('\n')
    out.close()
    filepath = os.path.join(os.getcwd(), 'genres.txt')
    println('[!] genre info written to %s' % filepath)


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
