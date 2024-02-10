from src import shared_funcions


def find_singles(spotify, sources):
    """
    Find all tracks from single or EP releases and list them to logs file.

    :param spotify:     spotipy object
    :param sources:     list of files with playlist ids
    :return: None
    """
    logs_file_name = 'logs/singles.log'
    with open(logs_file_name, "w") as f:
        f.write('')

    counter = 0
    passed_flag = True

    exceptions = shared_funcions.read_basic_exceptions('exceptions/singles.txt')  # Getting ids (only) of allowed singles
    playlist_ids = shared_funcions.read_sources(sources)  # Getting ids of playlists from sources

    # For every playlist: get track list
    # Then for every track on that list check if album_type is 'album'
    # Skip exeptions and print found singles to logs file
    for i, playlist_id in enumerate(playlist_ids):
        print(f'\rSingle finder: Checking playlist: {i + 1} / {len(playlist_ids)}', end='')

        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track'] is None:
                continue

            album_type = track['track']['album']['album_type']
            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']

            if track['track']['is_local']:
                continue
            if track_id in exceptions:
                continue

            if album_type != 'album':
                passed_flag = False
                counter += 1
                with open(logs_file_name, "a", encoding='utf-8') as f:
                    f.write(f'{track_id} from {album_type}: {artist_name} - {track_name} in {playlist_name}\n')
                #print(f'{album_type}: {artist_name} - {track_name} in {playlist_name}')
    print('\n')
    if passed_flag:
        print(f'Single finder: No sinles found')
    else:
        print(f'Single finder: Number of singles found: {counter}')

    return passed_flag
