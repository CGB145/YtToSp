import re
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import math
import numpy
from translate import Translator

def contains_hangul(text):
    # Define a pattern to match Hangul characters
    hangul_pattern = re.compile(r'[가-힣]')

    # Use the search method to find Hangul characters in the text
    if hangul_pattern.search(text):
        return True
    else:
        return False


def has_hangul_and_latin(text):
    hangul_pattern = re.compile(r'[가-힣]')
    latin_pattern = re.compile(r'[A-Za-z]')

    return bool(hangul_pattern.search(text) and latin_pattern.search(text))


def has_hangul_latin_and_parentheses(text):
    hangul_pattern = re.compile(r'[가-힣]')
    latin_pattern = re.compile(r'[A-Za-z]')
    parentheses_pattern = re.compile(r'\([^)]*\)')

    return (
        bool(hangul_pattern.search(text)) and
        bool(latin_pattern.search(text)) and
        bool(parentheses_pattern.search(text))
    )

def get_latin_text_in_parentheses(text):
    pattern = r'\(([^()]+)\)'  # Match Latin text inside parentheses

    matches = re.findall(pattern, text)

    if matches:
        extracted_text = matches[0]
        return extracted_text
    else:
        extracted_text = "No Latin text found in parentheses"

def get_hangul_text_in_parentheses(text):
    pattern = r'\(([^()가-힣]+)\)'  # Match Hangul text inside parentheses

    matches = re.findall(pattern, text)

    if matches:
        extracted_text = matches[0]
        return extracted_text
    else:
        extracted_text = "No Hangul text found in parentheses"

def has_hangul_text_in_parentheses(text):
    pattern = r'\([^)]*[가-힣][^)]*\)'  # Check for Hangul text inside parentheses

    match = re.search(pattern, text)

    if match:
        has_hangul_text = True
        return get_hangul_text_in_parentheses(text)
    else:
        has_hangul_text = False


def has_latin_text_in_parentheses(text):

    pattern = r'\([^)]*[A-Za-z][^)]*\)'  # Check for Latin text inside parentheses

    match = re.search(pattern, text)

    if match:
        has_latin_text = True
        return get_latin_text_in_parentheses(text)
    else:
        has_latin_text = False
        has_hangul_text_in_parentheses(text)

api_key = ""

youtube = build("youtube", "v3", developerKey=api_key)

scopes = ["ugc-image-upload", "user-read-playback-state","user-modify-playback-state","user-read-currently-playing","playlist-read-private","playlist-read-collaborative","playlist-modify-private","playlist-modify-public","user-library-modify","user-library-read"]


# Set up authentication and create a Spotipy client object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth()

user_id = sp.me()['id']


playlist_name = 'Caglan2'
playlist_description = ''
#playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)
playlist_list = sp.current_user_playlists(limit=50, offset=0)


repeat = len(playlist_list["items"])
i = 0
playlist_names = []
while i != repeat:
    playlist_names.append(playlist_list["items"][i]["name"])
    i += 1


index = playlist_names.index("Z")

playlist_id = playlist_list["items"][index]["id"]
playlist_track_len = sp.playlist_tracks(playlist_id=playlist_id)
playlist_track_len = playlist_track_len["total"]
i=0
print(playlist_track_len)
playlist_track_len = playlist_track_len/100
playlist_track_len = math.ceil(playlist_track_len)
playlist_track_list = []
offest_tracks = 0
while i != playlist_track_len:
    playlist_items_list = sp.playlist_items(playlist_id=playlist_id, fields=None,limit=100,offset=offest_tracks)
    loop_tracks = 0
    run = 0
    while loop_tracks != 100:
        try:
            playlist_track_list.append(playlist_items_list["items"][loop_tracks]["track"]["uri"])

            loop_tracks += 1


    
        except IndexError:
            break
    j=i
    i +=1
    if i == j+1:
        offest_tracks = i*100


playlist_track_list = numpy.array_split(playlist_track_list,5)
print(playlist_track_list)
i=0
while i!=len(playlist_track_list):
    sp.playlist_remove_all_occurrences_of_items(items=playlist_track_list[i],playlist_id=playlist_id)
    i += 1


youtube_playlist_id = "PLwhoLgTCNdqjU7Bh8iY1_QaBgKPUMdY-D"

playlistSnipept = youtube.playlistItems().list(part="contentDetails" ,playlistId=youtube_playlist_id)

totalVideo = playlistSnipept.execute()["pageInfo"]["totalResults"]


print(round(totalVideo/50))



request = youtube.playlistItems().list(part="contentDetails" ,playlistId=youtube_playlist_id, maxResults="50" )



x = request.execute()

max = len(x["items"])


j = 0

track_ids = []
track_ids2 = []
track_ids3 = []
list_of_tracks_not_found = []

while request is not None and j <= round(totalVideo/50):

    response = request.execute()

    for i in range(0, len(response["items"])):



        c = response["items"][i]["contentDetails"]["videoId"]

        z = youtube.videos().list(part = "snippet", id=f"{c}")
        y = z.execute()

        if len(y["items"]) > 0:
            title = y["items"][0]["snippet"]["title"]


            if has_latin_text_in_parentheses(title):
                title = has_latin_text_in_parentheses(title)
            if has_hangul_and_latin(title):
                title = re.sub(r'[가-힣]+', '', title)
                title = re.sub(r'\([^)]*\)', '', title)
            elif contains_hangul(title):
                translator = Translator(to_lang="en", from_lang="ko")
                title = translator.translate(title)  


            artist = y["items"][0]["snippet"]["channelTitle"]
            if has_hangul_and_latin(artist):
                artist = re.sub(r'[가-힣A-Za-z]+', '', artist)
            elif contains_hangul(artist):
                translator = Translator(to_lang="en", from_lang="ko")
                artist = translator.translate(artist)  

            pattern = " - Topic"
            artist = artist.replace(pattern, "")

            print(artist)
            results = sp.search(q=f"track:{title} artist:{artist}",type="track", market="DE")
            if results['tracks']['total'] > 0:
                track_id = results['tracks']['items'][0]['id']
                if len(track_ids) < 100:
                    track_ids.append(track_id)
                elif len(track_ids) == 100 and len(track_ids2) < 100:
                    track_ids2.append(track_id)
                elif len(track_ids) ==100 and len(track_ids2) == 100 and len(track_ids3) < 100:
                    track_ids3.append(track_id)

                print(f"Track ID: {track_id}")
            else:
                print("No tracks found.")
                list_of_tracks_not_found.append(title)
                list_of_tracks_not_found.append(artist)

            

            print(title)

    request = youtube.playlistItems().list_next(request, response)
    j += 1


print(list_of_tracks_not_found)
try:
    sp.playlist_add_items(playlist_id, track_ids)
    sp.playlist_add_items(playlist_id, track_ids2)
    sp.playlist_add_items(playlist_id, track_ids3)
except Exception:
    print("Done")


    
