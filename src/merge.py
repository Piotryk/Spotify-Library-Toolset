from src import shared_funcions


def merge(spotify, sources, target_id, add_in_doubt=False):
    """
    Gets all songs from sources playlists and add them to target playlist.
    Omits songs that are already there.
    Checks if there are similar songs (e.g. from single release).

    :param spotify:     spotipy object
    :param sources:     list of files with playlist ids
    :param target_id:   id of playlist where songs from sources will be added
    :param add_in_doubt:    True - adds songs even if song with similar name exists (e.g. same song from single)
    :return: None
    """
    logs_file_name = 'logs/merge.log'
    source_playlist_ids = shared_funcions.read_sources(sources)

    # Read all tracks from target
    target_track_list, target_playlist_name = shared_funcions.get_track_list(spotify, target_id)  # Get all tracks from playlist
    target_ids = [track['track']['id'] for track in target_track_list]
    target_songs = [{'name': track['track']['name'], 'id': track['track']['id'], 'artist_id': track['track']['artists'][0]['id']} for track in target_track_list]
    counter_local_songs = 0
    counter_similar_songs = 0
    counter_added_songs = 0
    found_similar = False

    with open(logs_file_name, "a") as f:
        f.write('')

    for i, playlist_id in enumerate(source_playlist_ids):
        source_track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist
        print(f'\rMerge: merging playlist: {i + 1} / {len(source_playlist_ids)}\t{playlist_name}', end='')

        for track in source_track_list:
            if track['track']['is_local']:
                with open(logs_file_name, "a") as f:
                    f.write(f"Local song: {track['track']['name']} from {playlist_name} skipped.\n")
                    counter_local_songs += 1
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']
            found_similar = False

            if track_id in target_ids:
                continue

            for song in target_songs:  # It can be done better
                if (track_name in song['name'] or song['name'] in track_name) and artist_id == song['artist_id']:
                    found_similar = True
                    if add_in_doubt:
                        spotify.playlist_add_items(target_id, [track_id])
                        counter_added_songs += 1
                        with open(logs_file_name, "a", encoding='utf-8') as f:
                            f.write(f'{track_id} {artist_name} - {track_name} from {playlist_name} added to {target_playlist_name} despite that ')
                            f.write(f'{song["name"]} by the same artist was already there.\n')
                    else:
                        with open(logs_file_name, "a", encoding='utf-8') as f:
                            f.write(f'{track_id} {artist_name} - {track_name} from {playlist_name} not added to {target_playlist_name} because ')
                            f.write(f'{song["name"]} by the same artist is already there.\n')
                    counter_similar_songs += 1
                break

            if found_similar:
                found_similar = False
                continue

            spotify.playlist_add_items(target_id, [track_id])
            counter_added_songs += 1
    print('', end='\n')

    print(f'Merge: {counter_added_songs} were added to {target_playlist_name}; {counter_local_songs} local files from sources skipped.')
    if add_in_doubt and counter_similar_songs:
        print(f'Merge: {counter_similar_songs} were also added to {target_playlist_name}')
    else:
        print(f'Merge: No songs with similar names were skipped')


def check_merged_simple(spotify, merged, sources):
    """
    Gets all tracks form merged playlists and check if they are in sources
    Checks sources for only specific version (based on track id)
    Missing songs will be listed in .log file

    :param spotify:     spotipy object
    :param merged:      list of files with playlist ids
    :param sources:     list of files with playlist ids
    :return: None
    """
    logs_file_name = 'logs/missing_from_sources_simple.log'
    with open(logs_file_name, "w") as f:
        f.write('')
    sources_ids = []

    counter_merged_local = 0
    counter_missing = 0

    merged_playlist_ids = shared_funcions.read_sources(merged)
    source_playlist_ids = shared_funcions.read_sources(sources)

    # Read all tracks from all sources
    for playlist_id in source_playlist_ids:
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track']['is_local']:
                continue

            track_id = track['track']['id']
            sources_ids.append(track_id)

    # Read tracks form merged and for every track check if its ID is in sources
    for i, playlist_id in enumerate(merged_playlist_ids):
        print(f'\rMerged playlists simple check: Checking playlist: {i + 1} / {len(merged_playlist_ids)}', end='')
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track']['is_local']:
                counter_merged_local += 1
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']

            if track_id not in sources_ids:
                with open(logs_file_name, "a", encoding='utf-8') as f:
                    f.write(f'{track_id} {artist_name} - {track_name} from {playlist_name} is nowhere to be found in sources.\n')
                    counter_missing += 1
    print('', end='\n')
    print(f'Merged playlists simple check: {counter_merged_local} local files skipped.')
    if counter_missing:
        print(f'Merged playlists simple check: {counter_missing} songs are missing from sources.')
    else:
        print(f'Merged playlists simple check: passed. All songs on merged are present in sources.')


# Gets all tracks form merged playlists and check if they are in sources.
# Also checks sources for songs with similar names. To find versions from different albums
# Missing songs will be listed in log file
def check_merged(spotify, merged, sources):
    """
    Gets all tracks form merged playlists and check if they are in sources
    Checks sources for same id and if there is a song with similar name by the same artist (artist check is based on id)
    Missing songs will be listed in .log file

    :param spotify:     spotipy object
    :param merged:      list of files with playlist ids
    :param sources:     list of files with playlist ids
    :return: None
    """
    logs_file_name = 'logs/missing_from_sources_full_check.log'
    with open(logs_file_name, "w") as f:
        f.write('')
    sources_songs = []
    sources_ids = []

    counter_merged_local = 0
    counter_missing = 0
    counter_missing_similar = 0
    similar_found = False

    merged_playlist_ids = shared_funcions.read_sources(merged)
    source_playlist_ids = shared_funcions.read_sources(sources)

    # Read all tracks from all sources
    for i, playlist_id in enumerate(source_playlist_ids):
        print(f'\rMerged playlists check: Reading source playlist: {i + 1} / {len(source_playlist_ids)}', end='')
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track']['is_local']:
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            sources_ids.append(track_id)
            sources_songs.append({'name': track_name, 'id': track_id, 'artist': artist_id, 'artist_name': artist_name, 'playlist_name': playlist_name, 'playlist_id': playlist_id})
    print('', end='\n')

    # Read tracks form merged and for every track check if it is in sources or look for similar names in sources
    for i, playlist_id in enumerate(merged_playlist_ids):
        print(f'\rMerged playlists check: Checking merged playlist: {i + 1} / {len(merged_playlist_ids)}', end='')
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        for track in track_list:
            if track['track']['is_local']:
                counter_merged_local += 1
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            if track_id in sources_ids:
                continue

            for song in sources_songs:  # It can be done better
                if (track_name in song['name'] or song['name'] in track_name) and artist_id == song['artist']:
                    with open(logs_file_name, "a", encoding='utf-8') as f:
                        f.write(f'Similar: {track_id} {artist_name} - {track_name} from {playlist_name} is not in sources, but: ')
                        f.write(f'song with similar name: {song["name"]} by the same artist is in {song["playlist_name"]}\n')
                    counter_missing_similar += 1
                    similar_found = True
                    break

            if similar_found:
                similar_found = False
                continue

            with open(logs_file_name, "a", encoding='utf-8') as f:
                f.write(f'Missing: {track_id} {artist_name} - {track_name} from {playlist_name} is nowhere to be found in sources.\n')
                counter_missing += 1
    print('', end='\n')

    print(f'Merged playlists check: {counter_merged_local} local files skipped.')
    if counter_missing or counter_missing_similar:
        print(f'Merged playlists check: {counter_missing} songs are completely missing from sources.')
        print(f'Merged playlists check: {counter_missing_similar} songs probably have different version on sources.')
    else:
        print(f'Merged playlists check: passed. All songs on merged are present in sources.')
