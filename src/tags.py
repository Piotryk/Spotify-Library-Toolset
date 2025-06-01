from src import shared_funcions

tag_data = {
        'S': {'aliases': ['src', 'source', 'sources'], 'exclusions': ['m', 'backup'], 'needs': []},
        'M': {'aliases': ['merged'], 'exclusions': ['s', 'backup'], 'needs': []},
        'P': {'aliases': ['przedawnione'], 'exclusions': ['s', 'm', 'backup'], 'needs': []},
        'Pom': {'aliases': ['pomidorki', 'pomidor', 'pomiudorek'], 'exclusions': ['s', 'm', 'backup'], 'needs': []},
        'BACKUP': {'aliases': [], 'exclusions': ['s', 'm', 'backup'], 'needs': []},
        'AR': {'aliases': [], 'exclusions': ['nieAR', 'D', 'PL'], 'needs': ['S']},
        'nieAR': {'aliases': ['nM'], 'exclusions': ['AR', 'D', 'PL'], 'needs': ['S']},
        'PL': {'aliases': [], 'exclusions': ['nieAR', 'D', 'PL'], 'needs': ['S']},
        'D': {'aliases': ['Durne'], 'exclusions': ['AR', 'nieAR', 'D', 'PL'], 'needs': ['S']},
        'BUG': {'aliases': [], 'exclusions': ['AR', 'nieAR', 'D', 'PL', 'S', 'M', 'BACKUP'], 'needs': []},
        'MD': {'aliases': [], 'exclusions': [], 'needs': ['S']},
        'VH': {'aliases': [], 'exclusions': [], 'needs': ['S']},
    }


def get_playlist_data(spotify):
    response = spotify.user_playlists((spotify.me())['id'])
    #print(f'Number of playlists on Spotify: {response["total"]}')
    total = response["total"]
    playlists = response['items']
    while response['next']:
        response = spotify.next(response)
        playlists.extend(response['items'])

    a = 0
    for i, playlist in enumerate(playlists):
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        print(f'\rGetting data from playlist: {i + 1} / {total}\t{playlist_name}', end='')

        tracks, _ = shared_funcions.get_track_list(spotify, playlist_id)
        playlist['tracks'] = tracks
    print('\n')

    return playlists


def check_if_tags_exist(spotify_data):
    """
    Prints out names of playlists with no tags.

    :param spotify:
    :return:
    """
    logs_file_name = 'logs/tags_missing.log'
    counter_with_tags = 0
    flag_missing_tags = False
    with open(logs_file_name, "w") as f:
        f.write('')

    with open(logs_file_name, 'a', encoding='utf-8') as f:
        for playlist in spotify_data:
            playlist_name = playlist['name']
            playlist_id = playlist['id']

            #response = spotify.playlist(playlist_id)
            desc = playlist['description']
            if 'Tags: ' not in desc:
                f.write(f'{playlist_name} is missing tags.\n')
                flag_missing_tags = True

    print("All playlist have tags.")
    return flag_missing_tags


def save_tags_to_logs(spotify_data):
    """
    Prints out names of playlists with no tags.

    :param spotify:
    :return:
    """
    logs_file_name = 'logs/tags.log'

    with open(logs_file_name, 'w', encoding='utf-8') as f:
        for playlist in spotify_data:
            playlist_name = playlist['name']
            playlist_id = playlist['id']
            playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
            
            name_len = 35
            from_playlist = playlist_name + ' ' * name_len
            from_playlist = from_playlist[:name_len]
            f.write(f'{playlist_id}\t{from_playlist}\tTags:\t{playlist_tags}.\n')

    print("All playlist tags saved to logs/tags.log.")


#TODO: Check for mutually exlusive tags
#TODO: Check if tag is already there
def add_tags_to_playlist(spotify, playlists, tag):
    """"
    Just adds a tag to playlist description.
    No checks if Tag is already there nor ffor mutually exlusive tags.

    :param spotify:     spotipy object
    :param playlists:   list of playlist ids
    :param tag:         str to add
    :return:            None
    """

    #FOR NOW THERE IS NO CHECK IF TAGS ARE NOT MUTUALLY EXCLUSIVE
    for playlist_id in playlists:
        response = spotify.playlist(playlist_id)
        desc = response['description']

        if 'Tags: ' in desc:
            desc = desc + ' ' + tag
        elif desc:
            desc = desc + ' Tags: ' + tag
        else:
            desc = 'Tags: ' + tag

        spotify.playlist_change_details(playlist_id, description=desc)

