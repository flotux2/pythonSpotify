import os
import sys
import urllib.request
import spotipy
import spotipy.util as util

username = '<USERNAME>' 
client_id = '<CLIENT_ID>'
client_secret = '<CLIENT_SECRET>'
redirect_uri = 'https://www.google.de/'
scope = 'user-library-read,playlist-modify-private,playlist-modify-public,playlist-read-private'

sidifyDirectory = '<SOURCE_DIRECTORY>'
searchForArtist = '<ARTIST>'

# Get token for access to Spotify
token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# Connect to Spotify
spotify = spotipy.Spotify(token)

results = spotify.search(q='artist:' + searchForArtist, type='artist')
items = results['artists']['items']

# No artist found
if len(items) == 0:
    print("[E] Artist not found.")
    exit

# Artist found - take the first one (hopefully the best choice)
else:
    artist = items[0]
    artistName = artist['name']

    # Replace special characters in the artist's name
    artistName = artistName.replace('?', '_')
    
    artistImageUrl = artist['images'][1]['url']
    artistFolderName = sidifyDirectory + artistName 
    artistImageFilename = artistFolderName + '/_' + artistName + '.jpg'
    playlistUrlsFilename = artistFolderName + '/PlaylistUrls.csv'

    # Create playlist file
    playlistUrlsFile = open(playlistUrlsFilename, 'a')

    # Print CSV header to playlist file
    print('Artist', 'Album', 'Playlist URL', sep=';', file=playlistUrlsFile)

    # Create artist folder
    try:
        if not os.path.exists(artistFolderName):
            os.makedirs(artistFolderName)
            print('[I] Artist directory "' + artistFolderName + '" has been created.')
        else:
            print('[W] Artist directory "' + artistFolderName + '" already exists.')
    except OSError:
        print('[E] Artist directory "' + artistFolderName + '" could not be created.') 

    # Download artist image if it doesn't already exist
    if not os.path.isfile(artistImageFilename):
        urllib.request.urlretrieve(artistImageUrl, artistImageFilename)
        print('[I] Artist image "', '_', artistName, '.jpg' ,  '" has been downloaded.', sep='')
    else:
        print('[W] Artist image "', '_', artistName, '.jpg' ,  '" already exists.', sep='')
    
    albums = []
    # Get albums and singles of the artist
    results = spotify.artist_albums(artist['id'], album_type='album,single')
    albums.extend(results['items'])

    # If search limit is hit, fetch next albums
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    # Sort albums by name
    #albums.sort(key=lambda album:album['name'].lower())

    # Sort albums by release date
    albums.sort(key=lambda album:album['release_date'])

    print('[I] ', len(albums), ' albums found for artist "', artistName, '".',  sep='')

    # Counter to use as prefix in the playlist name
    counter = 0

    # Iterate over all albums
    for album in albums:
        counter += 1
        albumId = album['id']
        albumName = album['name']

        # DEBUG: Print album name
        #print(albumName)
        
        # DEBUG: Skip album if it cannot be processed
        #if albumName == 'Benjamin Blümchen Liederzoo: Schokolade, Zuckerstückchen...':
            # Skip current album and continue with the next album
            #continue

        albumNameNormalized = albumName.replace(':', '_')
        albumNameNormalized = albumNameNormalized.replace('/', '_')
        albumNameNormalized = albumNameNormalized.replace('?', '_')
        albumNameNormalized = albumNameNormalized.replace('"', '')
        albumUri = album['uri']
        albumImageUrl = album['images'][1]['url']

        albumFolderName = sidifyDirectory + artistName + '/' + albumNameNormalized

        # Create album folder
        try:
            if not os.path.exists(albumFolderName):
                os.makedirs(albumFolderName)
                print('[I] Directory "' + albumFolderName + '" has been created.')
            else:
                print('[W] Directory "' + albumFolderName + '" already exists.')
        except OSError:
            print('[E] Directory "' + albumFolderName + '" could not be created.') 

        albumImageFilename = albumFolderName + '/_' + albumNameNormalized + '.jpg'

        # Download album image if it doesn't already exist
        if not os.path.isfile(albumImageFilename):
            urllib.request.urlretrieve(albumImageUrl, albumImageFilename)
            print('[I] Album image "', '_', albumNameNormalized, '.jpg' ,'" has been downloaded.', sep='')
        else:
            print('[W] Album image "', '_', albumNameNormalized, '.jpg' ,'" already exists.', sep='')

        # Create private playlist with title of album
        playlistName = str(counter) + ' - ' + artistName + ' - ' + albumName

        # Get playlists of user
        playlists = []        
        results = spotify.user_playlists(username, limit=50, offset=0)
        playlists.extend(results['items'])

        # Get next number of playlists if limit exceeded
        while results['next']:
            results = spotify.next(results)
            playlists.extend(results['items'])

        # Sort list of playlists by name
        playlists.sort(key=lambda playlist:playlist['name'].lower())

        # Playlist already exists
        if playlistName in [item['name'] for item in playlists]:
            print('[W] Playlist "', playlistName, '" already exits.', sep='')

        # Plalist does not exists.
        else:

            # Create playlist with name "artist - album"
            print('[I] Create playlist "', playlistName, '".', sep='')
            playlist = spotify.user_playlist_create(username, playlistName, public=False)
            playlistId = playlist['id']
            playlistUrl = playlist['external_urls']['spotify']
    
            tracks = []    
        
            # Add album tracks to the playlist
            for track in spotify.album_tracks(albumId)['items']:
                tracks.append(track["uri"])

            # Add tracks of the album to the playlist
            results = spotify.user_playlist_add_tracks(username, playlistId, tracks)

            # DEBUG - Output Artist, Album and Playlist URL    
            print(artistName, albumName, playlistUrl, sep=';')

            # Print playlist to playlist file
            print(artistName, albumName, playlistUrl, sep=';', file=playlistUrlsFile)

    # Loop over albums of artist

# Close playlist file        
playlistUrlsFile.close