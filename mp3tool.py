# coding: utf-8

import argparse
import eyed3
import eyed3.id3
import glob
import os
import sys

WINDOW_WIDTH = 120

excepts = (
	"In Flames",
)

words = (
	"a",
	"an", 
	"the", 

	"and",
	"or",
	
	"as",
	"at",
	"but",
	"by",
	"for",
	"in",
	"of",
	"off",
	"on",
	"per",
	"to",
	"up",
	"via",
	"yet", 

	"am",
	"was",
	"is",
	"are",
)

def println(output):
	if len(output) >= WINDOW_WIDTH:
		output = "%s..." % (output[0:WINDOW_WIDTH-3])
	output = unicode(output, "cp1251")
	try:
		if os.name == "nt":
			output = output.encode("cp866")
		print output
	except UnicodeEncodeError:
		pass

def get_folders(folder, alldirs):
	println("[!] Scanning: %s" % (folder))

	result = []
	hasSubdirs = False
	for item in os.listdir(folder):
		path = os.path.join(folder, item)
		if os.path.isdir(path):
			hasSubdirs = True
			result.extend(get_folders(path, alldirs))
	if not hasSubdirs or alldirs:
		result.append(folder)
	return result

def get_mp3_files(folder):
	println("[!] Scanning %s" % (folder))

	result = []
	items = glob.glob(os.path.join(folder, "*.mp3"))
	if items:
		result.extend(items)
	for item in os.listdir(folder):
		path = os.path.join(folder, item)
		if os.path.isdir(path):
			result.extend(get_mp3_files(path))
	return result

def replace(string):
	elements = string.split(os.sep)
	new_elements = []
	matches = (
		":%s", "-%s", "_%s", "%s(", ".%s", "%s(" 
	)
	for e in elements:
		for word in words:
			for exc in excepts:
				if word in exc.lower():
					continue
			old = " %s " % (word.capitalize())
			if e.count(old):
				skip = False
				for m in matches:
					if e.count(m % old):
						skip = True
						break
				if not skip:
					new = " %s " % (word)
					e = e.replace(old, new)
			old = " %s" % (word.capitalize())
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
				println("[!] file updated: %s" % (f))
			new_fname = replace(f)
			if f != new_fname:
				os.rename(f, new_fname)
				println("[!] file renamed: %s" % (f))
		except:
			println("[search_mp3] error: set tag for %s" % (f))

def search_folders(folder):
	folders = get_folders(folder, False)
	for item in folders:
		println(item)
		old_path = item
		new_path = replace(old_path)
		if old_path != new_path:
			os.rename(old_path, new_path)
			println("[!] folder renamed: %s" % (old_path))

def search_uncovered(folder):
	folders = get_folders(folder, False)
	for item in folders:
		covered = False
		for subitem in os.listdir(item):
			ext = os.path.splitext(subitem)[1]
			if ext in (".jpg", ".png", ".jpeg"):
				covered = True
		if not covered:
			println("[!] Uncovered: %s" % (item))

def search_genres(folder):
	tag = eyeD3.Tag()
	genres = {}
	folders = get_folders(folder, False)
	for item in folders:
		mp3s = glob.glob(os.path.join(item, "*.mp3"))
		if mp3s:
			println("[!] Processing %s..." % (item))
			path = mp3s[0]
			try:
				tag.link(path)
				genre = tag.getGenre().getName()
				if genre not in genres:
					genres[genre] = []
				genres[genre].append(item)
			except:
				println("[search_genres] error: get tag from %s" % (path))
	out = open("genres.txt", "w")
	for genre in genres:
		out.write(genre + ":\n")
		for item in genres[genre]:
			out.write(item + "\n")
		out.write("\n")
	out.close()
	filepath = os.path.join(os.getcwd(), "genres.txt")
	println("[!] genre info written to %s" % (filepath))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-F', dest='folder', type=str, required=True, help='Path to scanning')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-g', dest='genres', action='store_true', help='Collect genres')
	group.add_argument('-r', dest='rename', action='store_true', help='Rename directories')
	group.add_argument('-t', dest='tags', action='store_true', help='Fix ID3 tags.')
	group.add_argument('-u', dest='unusual', action='store_true', help='Search unusual ID3 attrs.')
	group.add_argument('-c', dest='covers', action='store_true', help='Search uncovered folders.')
	args = parser.parse_args()

	if args.tags:
		search_mp3(args.folder)
	elif args.rename:
		search_folders(args.folder)
	elif args.genres:
		search_genres(args.folder)
	elif args.unusual:
		search_unusual(args.folder)
	elif args.covers:
		search_uncovered(args.folder)
	return 0

if "__main__" == __name__:
	sys.exit(main())
