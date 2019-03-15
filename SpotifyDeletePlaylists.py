import spotipy
import spotipy.util as util

username = '<USERNAME>' 
client_id = '<CLIENT_ID>'
client_secret = '<CLIENT_SECRET>'
redirect_uri = 'https://www.google.de/'
scope = 'user-library-read,playlist-modify-private,playlist-modify-public,playlist-read-private'
searchString = '<SEARCH_STRING>'

# Get token for access to Spotify
token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# Connect to Spotify
spotify = spotipy.Spotify(token)
playlists = []
results = spotify.user_playlists(username, limit=50, offset=0)
playlists.extend(results['items'])

while results['next']:
    results = spotify.next(results)
    playlists.extend(results['items'])

# Iterate over playlists of the user
for playlist in playlists:
    playlistName = playlist["name"]

    # Check if playlist needs to be deleted based on the searchstring
    if searchString in playlistName:
        spotify.user_playlist_unfollow(username, playlist["id"])    
        print('Playlist "', playlistName, '" has been deleted.', sep='')
    
    # Skip playlist
    else:
        print('Skip playlist "', playlistName, '".', sep='')
