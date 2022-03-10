import requests 
import file_utils
import urllib3
import config_db
import os

def getFile(Lyrics_genre, song_dict, start=1):
	genre_label = config_db.GENRE_TO_LABEL[Lyrics_genre]
	genre_folder = config_db.LABEL_TO_PATH[genre_label]

	if not os.path.exists(genre_folder):
		os.makedirs(genre_folder)

	for i in range (start, 500):
		main_link = "https://www.lyrics.com/genre/" + Lyrics_genre

		print(f"[INFO] Current page: {i}, current genre: {genre_label}")

		if i > 1:
			main_link += "/"+ str(i)
		if Lyrics_genre == "Pop" and i > 1887 :
			return
		if Lyrics_genre == "Hip%20Hop" and i > 596:
			return
		if Lyrics_genre == "Electronic" and i > 881:
			return
		if Lyrics_genre == "Blues" and i > 217:
			return
		if Lyrics_genre == "Jazz" and i > 668:
			return
		if Lyrics_genre == "Funk%20--%20Soul" and i > 580:
			return

		content = requests.get(main_link, verify=False)
		content = content.text
		content = content.split("<p class=\"lyric-meta-title\">")[1:]
		for c in content:
			c = c.split("href=")[1]
			c = c.split(">")[0]
			c = c.replace("\"","")
			getLyrics(c, genre_label, genre_folder, song_dict) 

		# update dicts after each page
		file_utils.save_dict(song_dict)
		
def getLyrics(link, genre, folder, song_dict):
	link = "https://www.lyrics.com/" + link
	response = requests.get(link, verify=False)
	txt = response.text

	name = txt.split(" | ")[0]
	name = name.split("<title>")[1]
	name = name.split(" - ")[1].split("Lyrics")[0].strip()

	# don't deal with titles that are invalid filenames
	orig_name = name
	name = file_utils.get_valid_filename(name)
	if name is None:
		#print(f"[DEBUG] skipped {orig_name}")
		return
			
	ly = txt.split("data-lang=\"en\">")[1]
	ly = ly.split("</pre>")[0]
	ly = ly.split("</a>")
	clean_ly =""
	f = True
	for l in ly:
		for i in l:
			if i == "<":
				f = False
			if i == ">":
				f = True
				continue
			if f:
				clean_ly += i   

	response.close()

	# for valid names, write song lyrics if valid
	if not file_utils.is_content_valid(clean_ly):
		#print(f"[DEBUG] skipped {orig_name}, for content in non-English")
		return

	if name in song_dict:
		if genre in song_dict[name]: # exist in db
			return
		else: # exist on another genre
			song_dict[name] = song_dict[name] + [genre]
	else:
		song_dict[name] = [genre]

	song_path = os.path.join(folder, name + ".txt")
	f = open(song_path, "w")
	f.write(clean_ly)
	f.close()

def initialize():
	urllib3.disable_warnings()

	if not os.path.exists(config_db.DB_PATH):
		os.makedirs(config_db.DB_PATH)

	title_dict = file_utils.load_dict()

	getFile("Pop", title_dict) #1887
	getFile("Hip%20Hop", title_dict) #596
	getFile("Rock", title_dict) #2668
	getFile("Electronic", title_dict) #881
	getFile("Blues", title_dict) #217
	getFile("Jazz", title_dict) #668
	getFile("Funk%20--%20Soul", title_dict) #580

	print("[INFO] Finished initialization")

def finalize_DB():
	title_dict = file_utils.load_dict()
	file_utils.save_dict(title_dict, config_db.TITLES_GENRES_PATH)
	file_utils.save_stats()
	os.remove(config_db.TEMP_TITLES_GENRES_PATH)

#initialize()
#finalize_DB()
#print(file_utils.get_status())