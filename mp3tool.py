﻿# coding: utf-8

import argparse
import glob
import os
import sys

import terminal
import eyed3
import eyed3.id3


excepts = (
    'In Flames',
)

words = (
    'a', 'an', 'the',

    'and', 'or',

    'as', 'at', 'but', 'by',
    'for', 'in', 'of', 'off',
    'on', 'per', 'to', 'up',
    'via', 'yet',

    'am', 'was', 'is', 'are',
)


def println(output):
    window_width = terminal.get_terminal_width()
    if len(output) >= window_width:
        output = '%s…' % output[0:window_width - 1]
    output = unicode(output, 'cp1251')
    try:
        if os.name == 'nt':
            output = output.encode('cp866')
        print output
    except UnicodeEncodeError:
        pass


def get_folders(folder, alldirs):
    for root, dirs, files in os.walk(folder):
        if not files and not alldirs:
            continue
        println('[!] Scanning: %s' % root)
        yield root


def get_mp3_files(folder):
    def is_mp3(path):
        return os.path.splitext(path)[1] == '.mp3'

    for root, dirs, files in os.walk(folder):
        println('[!] Scanning %s' % root)
        for f in files:
            if is_mp3(f):
                yield os.path.join(root, f)


def replace(string):
    if not string:
        return None
    elements = string.split(os.sep)
    new_elements = []
    matches = (
        ':%s', '-%s', '_%s', '%s(', '.%s', '%s('
    )
    for e in elements:
        for word in words:
            for exc in excepts:
                if word in exc.lower():
                    continue
            old = ' %s ' % (word.capitalize())
            if e.count(old):
                skip = False
                for m in matches:
                    if e.count(m % old):
                        skip = True
                        break
                if not skip:
                    new = ' %s ' % word
                    e = e.replace(old, new)
        new_elements.append(e)
    return os.sep.join(new_elements)


def search_mp3(folder):
    files = get_mp3_files(folder)
    for f in files:
        try:
            tag = eyed3.load(f, eyed3.id3.ID3_V2_3).tag

            old_artist = tag.artist
            old_album = tag.album
            old_title = tag.title

            new_artist = replace(old_artist)
            new_album = replace(old_album)
            new_title = replace(old_title)

            changed = False
            if old_artist != new_artist:
                tag.artist = new_artist
                changed = True
            if old_album != new_album:
                tag.album = new_album
                changed = True
            if old_title != new_title:
                tag.title = new_title
                changed = True
            if changed:
                tag.save()
                println('[!] file updated: %s' % f)
            new_fname = replace(f)
            if f != new_fname:
                os.rename(f, new_fname)
                println('[!] file renamed: %s' % f)
        except (IOError, eyed3.id3.TagException):
            println('[search_mp3] error: set tag for %s' % f)


def search_folders(folder):
    folders = get_folders(folder, True)
    renamed_dirs = []
    for item in folders:
        old_path = item
        new_path = replace(old_path)
        if old_path != new_path:
            os.rename(old_path, new_path)
            renamed_dirs.append(old_path)
    println('')
    if renamed_dirs:
        for path in renamed_dirs:
            println('[!] folder renamed: %s' % path)
    else:
        println('[!] Nothing is renamed')


def search_uncovered(folder):
    folders = get_folders(folder, False)
    uncovered_dirs = []
    for item in folders:
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


def search_genres(folder):
    genres = {}
    folders = get_folders(folder, False)
    for item in folders:
        mp3s = glob.glob(os.path.join(item, '*.mp3'))
        if mp3s:
            path = mp3s[0]
            try:
                tag = eyed3.load(path, eyed3.id3.ID3_V2_3).tag
                if tag.genre:
                    genre = tag.genre.name
                    if genre not in genres:
                        genres[genre] = []
                    genres[genre].append(item)
                else:
                    println('[search_genres] error: not genre in %s' % path)
            except IOError:
                println('[search_genres] error: get tag from %s' % path)
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
    parser.add_argument('-F', dest='folder', type=str, required=True, help='Path to scanning')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', dest='genres', action='store_true', help='Collect genres')
    group.add_argument('-r', dest='rename', action='store_true', help='Rename directories')
    group.add_argument('-t', dest='tags', action='store_true', help='Fix ID3 tags.')
    group.add_argument('-c', dest='covers', action='store_true', help='Search uncovered folders.')
    args = parser.parse_args()

    if args.tags:
        search_mp3(args.folder)
    elif args.rename:
        search_folders(args.folder)
    elif args.genres:
        search_genres(args.folder)
    elif args.covers:
        search_uncovered(args.folder)
    return 0


if '__main__' == __name__:
    sys.exit(main())
