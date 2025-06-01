import operator
from src import shared_funcions

#TODO make better logs for copy poaste to exceptions
def find_duplicaded_songs(spotify_data, tags=None, use_exceptions=True):
    """
    Finds songs that are on more than one playlist.
    Found cases are saved to a file.

    :param spotify:     spotipy object
    :param tags:        list of tags. Only playlists with provided tags will be checked
    :param use_exceptios:      
    :return: None
    """
    logs_file_name = 'logs/duplicated_songs.log'
    songs = {}
    counter_duplicates = 0

    exceptions = {}
    exceptions = shared_funcions.read_exceptions_with_playlist('exceptions/multi_source_songs.txt')  # Getting ids of allowed songs

    for i, playlist in enumerate(spotify_data):
        playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
        if tags:
            tag_in_desc = any([tag in playlist_tags for tag in tags])
            if not tag_in_desc:     # If there is no tag skip playlist
                continue

        for track in playlist['tracks']:
            if track['track'] is None:
                print(track)
                continue
            
            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']

            if use_exceptions and (playlist['id'], track_id) in exceptions:
                continue


            name_len = 45
            track_name = f'{artist_name} - {track_name}' + ' ' * name_len
            track_name = track_name[:name_len]
            name_len = 22
            playlist_name = f"{playlist['name']}" + ' ' * name_len
            playlist_name = playlist_name[:name_len]
            if track['track']['is_local']:
                track_id = track_name + ' ' * 22
                track_id = track_name[:22]

            if track_id in songs:
                songs[track_id]['playlists'][playlist['id']] = playlist_name
            else:
                name_len = 20   
                songs[track_id] = {}
                songs[track_id]['playlists'] = {playlist['id']: playlist_name}
                songs[track_id]['id'] = track_id
                songs[track_id]['name'] = track_name
                
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')                    
        for song in songs:
            if len(songs[song]['playlists']) > 1:
                counter_duplicates = counter_duplicates + 1
                log_file.write(f"{songs[song]['id']}\t{songs[song]['name']}\ton playlists: {songs[song]['playlists']}\n")

    if counter_duplicates:
        print(f'Duplicate song finder: Number of duplicated songs found: {counter_duplicates}')
    else:
        print(f'Duplicate song finder: Success. No duplicated songs found.')

    return counter_duplicates


#TODO: Make excemptions based on specific songs not artists.
def find_duplicated_artists(spotify_data, tags=None, use_exceptions=True):
    """
    Finds songs that are on more than one playlist.
    Found cases are saved to a file.

    :param spotify:     spotipy object
    :param tags:        list of tags. Only playlists with provided tags will be checked
    :param use_exceptios:      
    :return: None
    """
    logs_file_name = 'logs/duplicated_artists.log'
    artists = {}
    counter_duplicates = 0

    exceptions = {}
    exceptions = shared_funcions.read_exceptions_with_playlist('exceptions/multi_source_artists.txt')  # Getting ids of allowed artists
    for i, playlist in enumerate(spotify_data):
        playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
        if tags:
            tag_in_desc = any([tag in playlist_tags for tag in tags])
            if not tag_in_desc:   
                continue

        for track in playlist['tracks']:

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            if use_exceptions and (playlist['id'], artist_id) in exceptions:     # exceptions for artists are per artists :/ 
                continue

            name_len = 45
            track_name = f'{artist_name} - {track_name}' + ' ' * name_len
            track_name = track_name[:name_len]
            name_len = 22
            playlist_name = f"{playlist['name']}" + ' ' * name_len
            playlist_name = playlist_name[:name_len]
            name_len = 22
            artist_name = artist_name + ' ' * name_len
            artist_name = artist_name[:name_len]
            if track['track']['is_local']:
                artist_id = track_name + ' ' * 22
                artist_id = track_name[:22]

            if artist_id in artists:
                artists[artist_id]['playlists'][playlist['id']] = playlist_name
            else:
                name_len = 20   
                artists[artist_id] = {}
                artists[artist_id]['playlists'] = {playlist['id']: playlist_name}
                #artists[artist_id]['playlists'][playlist['id']] = {playlist['id']: playlist_name}
                #artists[artist_id]['playlists']['list'] = {playlist['id']: playlist_name}
                artists[artist_id]['id'] = artist_id
                artists[artist_id]['name'] = artist_name
                
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')                    
        for artist in artists:
            if len(artists[artist]['playlists']) > 1:
                counter_duplicates = counter_duplicates + 1
                log_file.write(f"{artists[artist]['id']}\t{artists[artist]['name']}\ton playlists: {artists[artist]['playlists']}\n")

    if counter_duplicates:
        print(f'Duplicate artist finder: Number of duplicated artist found: {counter_duplicates}')
    else:
        print(f'Duplicate artist finder: Success. No duplicated artists found.')

    return counter_duplicates
    

def check_for_similar_names(spotify_data, tags=None, use_exceptions=True):
    """
    Finds songs with simialr names.
    Mainly searching for:
    Blah - remastered / (cover) / - 20xx version etc.

    :param spotify:     spotipy object
    :param tags:        list of tags. Only playlists with provided tags will be checked
    :param use_exceptios:      
    :return: None
    """

    tracks = []
    counter_similar = 0
    logs_file_name = 'logs/duplicates_by_name.log'
    
    exceptions = {}
    exceptions = shared_funcions.read_exceptions_with_playlist('exceptions/duplicates_by_name.txt')  # 

    for i, playlist in enumerate(spotify_data):
        playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
        tag_in_desc = any([tag in playlist_tags for tag in tags])
        if not tag_in_desc:     # If there is no tag in desc skip playlist
            continue

        for track in playlist['tracks']:
            #\if track['track'] is None:
            #    continue
            if track['track']['is_local']:
                track['track']['id'] = track['track']['name'].split()[0]
            track['playlist'] = playlist['name']
            tracks.append(track)
    # D:
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')   
        for track in tracks:
            for other_track in tracks:
                if track['track']['id'] == other_track['track']['id']:
                    continue
                if use_exceptions and ((track['track']['id'], other_track['track']['id']) in exceptions or (other_track['track']['id'], track['track']['id']) in exceptions):     # exceptions for artists are per artists :/ 
                    continue

                if track['track']['artists'][0]['name'] == other_track['track']['artists'][0]['name'] and (track['track']['name'] in other_track['track']['name'] or other_track['track']['name'] in track['track']['name']) :
                    counter_similar = counter_similar + 1
                    name_len = 45
                    name = f"{track['track']['artists'][0]['name']} - {track['track']['name']}{' ' * name_len}"[:name_len]
                    other_track_name = f"{other_track['track']['artists'][0]['name']} - {other_track['track']['name']}{' ' * name_len}"[:name_len]
                    
                    log_file.write(f"{track['track']['id']} {other_track['track']['id']} - {name}\t/\t{other_track_name} on {track['playlist']} / {other_track['playlist']}\n")
    
    if counter_similar:
        print(f'Duplicate finder: Number of songs with similar names: {counter_similar}')
    else:
        print(f'Duplicate finder: Success. No similar names found.')

    return counter_similar
