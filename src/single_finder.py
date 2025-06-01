from src import shared_funcions

def find_singles(spotify_data, tags=None, use_exceptions=True):
    """
    Find all tracks from single or EP releases and list them to logs file.
    Finder will only look on playlist with specific tags if provided.

    :param spotify_data:    list of playlist_data
    :param tags:            list of tags (str).
    :return: None
    """
    logs_file_name = 'logs/singles.log'
    counter_singles = 0
    passed_flag = True

    exceptions = shared_funcions.read_basic_exceptions('exceptions/singles.txt')  # Getting ids (only) of allowed singles

    # For every playlist: 
    # For every track on that list check if album_type is 'album'
    # Skip exeptions and print found singles to logs file
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')
        for i, playlist in enumerate(spotify_data):
            playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
            if tags:
                tag_in_desc = any([tag in playlist_tags for tag in tags])
                if not tag_in_desc:     # If there is no tag skip playlist
                    continue

            for track in playlist['tracks']:
                if track['track'] is None:
                    continue

                track_id = track['track']['id']
                track_name = track['track']['name']
                album_type = track['track']['album']['album_type']
                artist_name = track['track']['artists'][0]['name']

                if track['track']['is_local']:
                    continue
                if use_exceptions and track_id in exceptions:
                    continue

                if album_type != 'album':
                    passed_flag = False
                    counter_singles += 1
                    # Weird formatting stuff
                    name_len = 45
                    name = f'{artist_name} - {track_name}' + ' ' * name_len
                    name = name[:name_len]
                    space = '\t'        #why?
                    if album_type == 'single':
                        space = '\t\t'

                    log_file.write(f'{track_id}\tfrom {str(album_type).title()}:{space}{name}\ton {playlist["name"]}\n')

    if counter_singles:
        print(f'Single finder: Number of singles found: {counter_singles}')
    else:
        print(f'Single finder: Success. No singles found.')

    return passed_flag

