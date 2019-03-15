import os
import sys
import urllib.request
import spotipy
import spotipy.util as util

username = '<USERNAME>' 
client_id = '<CLIENT_ID>'
client_secret = '<CLIENT_SECRET>'
redirect_uri = 'https://www.google.de/'
scope = 'user-library-read,playlist-modify-private,playlist-modify-public'

# Get token for access to Spotify
token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# Connect to Spotify
spotify = spotipy.Spotify(token)
artist = spotify.artist("<SPOTIFY_URL_OF_ARTIST")
print(artist['id'])
albums = []
results = spotify.artist_albums(artist['id'], album_type='album,single')
albums.extend(results['items'])

while results['next']:
    results = spotify.next(results)
    albums.extend(results['items'])

albums.sort(key=lambda album:album['name'].lower())

for album in albums:
    name = album['name']
    print((' ' + name))

print(len(albums))