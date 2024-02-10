import operator
from src import shared_funcions


def find_duplicaded_songs(spotify, sources):
    """
    Finds songs that are on more than one playlist.
    Found cases are saved to a file.

    :param spotify:     spotipy object
    :param sources:     list of files with playlist ids
    :return: None
    """
    logs_file_name = 'logs/duplicated_songs.log'
    with open(logs_file_name, "w") as f:
        f.write('')

    #song_ids = []
    songs = []
    counter_duplicates = 0
    counter_similar_names = 0

    exceptions = shared_funcions.read_exceptions_with_playlist('exceptions/multi_source_songs.txt')  # Getting ids of allowed songs
    playlist_ids = shared_funcions.read_sources(sources)  # Getting ids of playlists from sources

    for i, playlist_id in enumerate(playlist_ids):
        print(f'\rDuplicated songs check: Checking playlist: {i+1} / {len(playlist_ids)}', end='')

        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track']['is_local']:
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            if (track['track']['id'], playlist_id) in exceptions:
                songs.append({'name': track_name, 'id': track_id, 'artist': artist_id, 'artist_name': artist_name, 'playlist': playlist_name, 'playlist_id': playlist_id})
                # ^ It has to be here. It causes double entries in exeptions sometimes, I'm not sure if it will work in all cases without that
                continue

            #ids = [song['id'] for song in songs]
            for song in songs:  # It can be done better
                if track_id == song['id']:
                    with open(logs_file_name, "a", encoding='utf-8') as f:
                        f.write(f'{track_id} {playlist_id} : {artist_name} - {track_name} from {playlist_name}\n')
                        f.write(f'found in {song["playlist"]} {song["playlist_id"]}\n')
                    counter_duplicates += 1
                    break
                if (track_name in song['name'] or song['name'] in track_name) and artist_id == song['artist']:
                    with open(logs_file_name, "a", encoding='utf-8') as f:
                        f.write(f'{track_id} {playlist_id} : {artist_name} - {track_name} from {playlist_name}\n')
                        f.write(f'song with similar name: {song["name"]} in {song["playlist"]} {song["id"]} {song["playlist_id"]}\n')
                    counter_similar_names += 1
                    break

            songs.append({'name': track_name, 'id': track_id, 'artist': artist_id, 'artist_name': artist_name, 'playlist': playlist_name, 'playlist_id': playlist_id})

    print('', end='\n')
    if counter_duplicates or counter_similar_names:
        print(f'Duplicated songs check: Obvious duplicates found: {counter_duplicates}')
        print(f'Duplicated songs check: Possible duplicates found: {counter_similar_names}')
    else:
        print(f'Duplicated songs check: passed. No duplicates found.')


def find_duplicated_artists(spotify, sources):
    """
    Finds artists that are on more than one playlists
    Exceptions are based on specific songs

    :param spotify:     spotipy object
    :param sources:     list of files with playlist ids
    :return: None
    """
    logs_file_name = 'logs/duplicated_artists.log'
    with open(logs_file_name, "w") as f:
        f.write('')

    artists = []
    artist_ids = []
    counter_duplicates = 0
    exceptions = shared_funcions.read_exceptions_with_playlist('exceptions/multi_source_artists.txt')  # Getting ids of allowed songs
    playlist_ids = shared_funcions.read_sources(sources)  # Getting ids of playlists from sources

    # Get data for all playlists without checking for duplicates yet
    for i, playlist_id in enumerate(playlist_ids):
        print(f'\rDuplicated artists check: Checking playlist: {i + 1} / {len(playlist_ids)}', end='')
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            if track['track']['is_local']:
                continue

            if (track['track']['id'], playlist_id) in exceptions:
                continue

            if artist_id in artist_ids:
                i = artist_ids.index(artist_id)
                if playlist_id not in artists[i]['playlist_ids']:
                    counter_duplicates += 1
                    artists[i]['song_names'].append(track_name)
                    artists[i]['song_ids'].append(track_id)
                    artists[i]['playlist_ids'].append(playlist_id)
                    artists[i]['playlist_names'].append(playlist_name)
                    with open(logs_file_name, 'a', encoding='utf-8') as f:
                        f.write(f'{track_id} {playlist_id} : {artist_name} - {track_name} from {playlist_name} is potential exception. ')
                        f.write(f'{artist_name} populate: {artists[i]["playlist_names"]}\n')
            else:
                artist_ids.append(artist_id)
                artists.append({'id': artist_id,
                                'name': artist_name,
                                'playlist_ids': [playlist_id],
                                'playlist_names': [playlist_name],
                                'song_names': [track_name],
                                'song_ids': [track_id],
                                })
    print('', end='\n')

    # Check for duplicates
    artists.sort(key=operator.itemgetter('name'))
    with open(logs_file_name, 'a', encoding='utf-8') as f:
        if counter_duplicates:
            f.write('\n\n\n\n\n')
        for artist in artists:
            if len(artist['playlist_ids']) > 1:
                f.write(f'{artist["id"]} {artist["name"]} found on {len(artist["playlist_ids"])} playlists:\n')
                for name in artist['playlist_names']:
                    f.write(f'{name}\n')

    if counter_duplicates:
        print(f'Duplicated artists check: Found {counter_duplicates} artists on two or more playlists')
    else:
        print(f'Duplicated artists check: passed. No duplicates found.')
