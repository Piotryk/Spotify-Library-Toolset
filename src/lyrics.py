import re
import os
import lyricsgenius

import config
from src import shared_funcions


def clean_title(title):
    #title = title['name'].lower()

    # general checks for 'feats', 'remaster' etc.
    title = re.sub(' -.*', '', title)  # Removes ' - Remastered' and similar things from title (reissue, rearmed, remaster)
    title = re.sub('\[?\(?[fF]eat.*', '', title)
    title = re.sub('[\[.*\]]', '', title)

    # Very specific checks mainly for specific songs
    title = re.sub(" ?\(Metal [Cc]over.*", '', title)
    title = re.sub(" ?\(Metal [Vv]ersion.*", '', title)
    title = re.sub(" ?\(Dave Cobb Session.*", '', title)
    return title


def get_ids_from_lyrics_file(file_name):
    ids = []

    if not os.path.isfile(file_name):
        return ids

    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue
            if line[0] != '#':
                continue
            line = line.split()
            ids.append(line[1])
    return ids


def get_lyrics_from_playlist(playlist_data, genius, skip_ids, exceptions, logs_file_name='logs/lyrics.log', data_file_name='data/lyrics.txt'):
    """
    Downloads lyrics for all songs on a playlist and saves them to one file.
    Lyrics file format:
    # {id}
    {artist} - {title}
    \n
    {lyrics}
    \n

    :param spotify:
    :param genius:
    :param playlist_id:
    :param skip_ids:
    :param exceptions:
    :param logs_file_name:
    :param data_file_name:
    :return:
    """
    counter_nothing_found = 0
    counter_wrong_lyrics = 0
    counter_mismatch = 0
    counter_added = 0

    track_list = playlist_data['tracks']
    playlist_name = playlist_data['name']

    with open(logs_file_name, "a", encoding='utf-8') as log_file:
        log_file.write('')   
        log_file.write(f'Lyrics: Downloading lyrics for: {playlist_name}\n')
        for track in track_list:
            if track['track']['is_local']:
                #continue
                song_id = 'Local song            '
                title = track['track']['name']
                artist_name = ''
            else:
                song_id = track['track']['id']
                title = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
            title = clean_title(title)

            if song_id in skip_ids:  # Skip songs that already have lyrics downloaded
                continue

            if song_id in exceptions:  # Skip songs: instrumental etc.
                continue

            # Get lyrics from genius
            # Try/except because of potencial Timeout Errors from api/requests
            try:
                song_genius = genius.search_song(title, artist_name, get_full_info=False)
            except BaseException:  # exceptions for timeouts
                log_file.write(f'{song_id} Timeout ERROR for: {artist_name} - {title}\n')
                continue

            if song_genius is None:  # No results of search
                log_file.write(f'{song_id}\t{artist_name} - {title}: Nothing found\n')
                counter_nothing_found += 1
                continue

            lyrics = song_genius.lyrics
            lyrics = re.sub('.*[Cc]ontributors.*Lyrics', '', lyrics)  # cleaning first line data
            lyrics = re.sub('\d*[Ee]mbed', '', lyrics)  # cleaning last line data
            artist_genius = song_genius.artist
            title_genius = song_genius.title
            title_genius = re.sub('’', '\'', title_genius)  # changing genius apostrophe to spotify to avoid differences in titles

            # Genius serch sometimes returns lyrics for a show? Disregarding those results
            if len(lyrics) > 10000:
                log_file.write(f'{song_id}\t{artist_name} - {title}: Wrong lyrics found. Found: {artist_genius} - {title_genius}\n')
                counter_wrong_lyrics += 1
                continue

            # If both artist and title are different, then the lyrics are most probably wrong too. Skipping
            # Unfortunately makes a few cases where lyrics where accurate. Change logic?
            if artist_name.lower() != artist_genius.lower() and title.lower() != title_genius.lower():
                log_file.write(f'{song_id}\t{artist_name} - {title}: Wrong lyrics found. Found: {artist_genius} - {title_genius}\n')
                counter_wrong_lyrics += 1
                continue

            # Checking what causes slight mismatch between search and result values. Lyrics are probably ok so adding them to file anyway
            if artist_name.lower() != artist_genius.lower() or title.lower() != title_genius.lower():
                log_file.write(f'Mismatch of names. Searched for: {artist_name} - {title}. Found: {artist_genius} - {title_genius}\n')
                counter_mismatch += 1
                continue

            # Add lyrics to file
            with open(data_file_name, "a", encoding='utf-8') as f:
                f.write(f'# {song_id}\n')
                f.write(f'{artist_genius} - {title_genius}\n\n')
                f.write(lyrics)
                f.write(f'\n\n\n\n\n')

            skip_ids.append(track['track']['id'])
            counter_added += 1
            log_file.write(f'Adding: {artist_name} - {title} to {playlist_name}\n')

    return counter_added, counter_nothing_found, counter_wrong_lyrics, counter_mismatch


def get_lyrics(spotify_data, tags, check_existing_file=True, preserve_logs=False):
    """
    Downloads lyrics for all songs on one playlist and saves them to one file.
    Downloading itself is in get_lyrics()
    :param spotify:     spotipy object
    :param playlist_id:
    :param check_existing_file: True - read lyrics file for already downloaded songs, False - clear lyrics file before downloading new songs
    :param preserve_logs: False - clear .log file
    :return: None
    """
    genius = lyricsgenius.Genius(config.GENIUS_KEY, response_format='plain', remove_section_headers=True, skip_non_songs=True)
    genius.verbose = False  # Turn off status messages

    logs_file_name = 'logs/lyrics.log'
    data_file_name = 'lyrics.txt'
    exceptions_file_name = 'exceptions/lyrics.txt'

    existing_song_ids = []
    if check_existing_file:
        existing_song_ids = get_ids_from_lyrics_file(data_file_name)

    exceptions = shared_funcions.read_basic_exceptions(exceptions_file_name)  # Not neccesery. Only to shorten .log file

    if not preserve_logs or not os.path.isfile(logs_file_name):
        with open(logs_file_name, "w") as f:    # I want to preserve logs from previous run in case of updating
            f.write('')
    if not check_existing_file or not os.path.isfile(data_file_name):
        with open(data_file_name, "w") as f:
            f.write('')

    for playlist in spotify_data:
        playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
        if tags:
            tag_in_desc = any([tag in playlist_tags for tag in tags])
            if not tag_in_desc:     # If there is no tag skip playlist
                continue

        counter_added, counter_nothing_found, counter_wrong_lyrics, counter_mismatch = \
            get_lyrics_from_playlist(playlist, genius, existing_song_ids, exceptions, logs_file_name=logs_file_name, data_file_name=data_file_name)

    if check_existing_file:
        print(f'Lyrics: Lyrics file updated. {counter_added} songs added to {data_file_name}.')
    else:
        print(f'Lyrics: Lyrics file created. {counter_added} songs added to {data_file_name}.')

    if counter_nothing_found or counter_wrong_lyrics or counter_mismatch:
        print(f'Lyrics: No lyrics found for {counter_nothing_found} songs.')
        print(f'Lyrics: Wrong lyrics found for {counter_wrong_lyrics} songs.')
        print(f'Lyrics: Mismatched name for {counter_wrong_lyrics} songs.')

