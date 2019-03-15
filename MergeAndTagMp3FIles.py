import sys
import os
import glob
import re
from mutagen.id3 import ID3, TIT2, TALB, TCON, TRCK
import ffmpy

startDirectory = '<YOUR_START_DIRECTORY>'

trackNumber = '01'
genre = '<GENRE>'


# Get subdirectories with albums
subDirectories = glob.glob(startDirectory + '/*' + os.path.sep)

# Iterate over album folders 
for subDirectory in subDirectories:

    # Get all single MP3 files of the current directory
    singleMp3Files = glob.glob(subDirectory + "*.mp3")

    # Concatenate all filenames to one string, use separator "|"
    singleMp3FilesString = '|'.join(singleMp3Files)

    mergedMp3Filename = subDirectory + 'output.mp3'

    # Build ffmpeg command to merge single MP3 files to one MP3 file
    ffmpeg = ffmpy.FFmpeg(
        inputs={'concat:' + singleMp3FilesString: None},
        outputs={mergedMp3Filename: '-acodec copy'}
    )

    # DEBUG: Output ffmpeg command to merge single MP3 files to one MP3 file
    #print(ffmpeg.cmd)
    
    # Run ffmpeg command
    ffmpeg.run()

    # Reference to ID3 tags of merged MP3 file
    mergedMp3File = ID3(mergedMp3Filename)

    # Get album title from ID3 tag
    albumTitleId3Tag = mergedMp3File['TALB'].text[0]
    
    # Get artist from ID3 tag
    artistId3Tag = mergedMp3File['TPE1'].text[0]

    # Regular expression to get episode number and episode title out of album title
        matchObject = re.match( r'^(\d{2,3})_(.+)', albumTitleId3Tag)

    # Get episode number with regular expression
    episodeNumber = matchObject.group(1)
    
    # Get episode title with regular expression
    episodeTitle = matchObject.group(2)

    albumTitleNew = artistId3Tag + ' ' + episodeNumber

    # Change ID3 tags
    mergedMp3File['TALB'].text[0] = albumTitleNew
    #mergedMp3File['TCON'].text[0] = 'Hörspiel'
    mergedMp3File.add(TCON(text=genre))

    #audio.add(TIT2(encoding=3, text=u"An example"))

    mergedMp3File['TRCK'].text[0] = trackNumber
    mergedMp3File['TIT2'].text[0] = episodeTitle
   
    # Save changed ID3 tags
    mergedMp3File.save()

    # Rename merged MP3 file
    targetFilename = startDirectory + '/' + trackNumber + ' - ' + albumTitleNew + ' - ' + artistId3Tag + ' - ' + episodeTitle + '.mp3'
    print(targetFilename)
    os.rename(mergedMp3Filename, targetFilename)

# Iterate over album folders    