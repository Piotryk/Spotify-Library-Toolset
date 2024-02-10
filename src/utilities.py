from src import shared_funcions


def get_artists_to_file(spotify, playlist_ids):
    """
    Save all artists from a list of playlists to a file for filling monthly listeners data later
    file structure:
    id  name
    :param spotify:
    :param playlist_ids: list of ids
    :return:
    """
    file = 'data/artists.txt'
    #artists = [{'id': track['track']['artists'][0]['id'], 'name': track['track']['artists'][0]['name']} for track in track_list if not track['track']['is_local']]
    artists = []
    artist_ids = []
    for playlist_id in playlist_ids:
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)
        for track in track_list:
            if track['track']['is_local']:
                continue
            if track['track']['artists'][0]['id'] in artist_ids:
                continue

            artists.append({'id': track['track']['artists'][0]['id'], 'name': track['track']['artists'][0]['name']})
            artist_ids.append(track['track']['artists'][0]['id'])

    with open(file, "w", encoding='utf-8') as f:
        f.write('')
        for artist in artists:
            f.write(f'{artist["id"]}\t{artist["name"]}\n')


def make_artist_playlist(spotify, artist_id):
    """
    WORK IN PROGRESS. DO NOT USE
    Keep singles and EPs

    :param spotify:
    :param artist_id:
    :return:
    """
    '''
    response = spotify.artist_albums(artist_id, album_type=None, country=None, limit=20, offset=0)
    #artist_name = response['name']
    album_list = response['items']
    while response['next']:
        response = spotify.next(response)
        album_list.extend(response['items'])
    albums = [album for album in album_list if album['album_group'] != 'appears_on']
    '''
    pass


# Depreceated
# Agressively checking if ids are still valid by opening them in webbrowser :)
def check_ids(ids):
    import webbrowser
    for id in ids:
        url = 'https://open.spotify.com/playlist/' + str(id)
        webbrowser.open_new_tab(url)


# Depreceated
def add_missing_from_check(spotify):
    target = '2iOpIZ2RlsyzZYksPzgKPv'
    file = 'logs/missing_from_sources_full_check.txt'
    song_ids = []
    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue
            line = line.split()
            song_ids.append(line[1])
    print(song_ids)
    #spotify.playlist_add_items(target, song_ids)
    for song_id in song_ids:
        spotify.playlist_add_items(target, [song_id])


# Depreceated
def remove_from_all(spotify, target):
    file = 'logs/missing_from_sources_full_check.txt'
    song_ids = []
    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue
            line = line.split()
            song_ids.append(line[1])
    print(song_ids)
    # spotify.playlist_add_items(target, song_ids)
    for song_id in song_ids:
        spotify.playlist_remove_all_occurrences_of_items(target, [song_id])
