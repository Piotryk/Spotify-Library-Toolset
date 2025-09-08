from src import shared_funcions


def get_track_ids_with_tags(spotify_data, tags):
    """

    :param spotify_data:
    :param tags:           list of str
    :return:               list of dicts     ids from playlist with any of tags. Possible duplicates
    """
    tracks = []
    for i, playlist in enumerate(spotify_data):
        playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
        tag_in_desc = any([tag in playlist_tags for tag in tags])
        if not tag_in_desc:     # If there is no tag in desc skip playlist
            continue

        for track in playlist['tracks']:
            if track['track'] is None:
                continue
            if track['track']['is_local']:
                continue
            track['playlist'] = playlist['name']
            tracks.append(track)

    return tracks


def check_merged(spotify_data, merge_tags, source_tags):
    """

    :param spotify_data:
    :param tags:           list of str
    :return:
    """
    source_tracks = get_track_ids_with_tags(spotify_data, source_tags)
    source_ids = [track['track']['id'] for track in source_tracks]
    merge_tracks = get_track_ids_with_tags(spotify_data, merge_tags)

    logs_file_name = 'logs/merge_check.log'
    counter_missing_from_sources = 0

    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')
        for i, track in enumerate(merge_tracks):
            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            from_playlist = track['playlist']
            if track_id not in source_ids:
                counter_missing_from_sources = counter_missing_from_sources + 1
                # Weird formatting stuff
                name_len = 45
                name = f'{artist_name} - {track_name}' + ' ' * name_len
                name = name[:name_len]

                name_len = 35
                from_playlist = from_playlist + ' ' * name_len
                from_playlist = from_playlist[:name_len]
                # f.write(f'{track_id}\tfrom {str(album_type).title()}: {artist_name} - {track_name}\ton {playlist["name"]}\n')
                log_file.write(f'{track_id}\t{name}\ton {from_playlist}\t is missing from sources.\n')

    if counter_missing_from_sources:
        print(f'Merged simple check: Number of missing from sources: {source_tags}: {counter_missing_from_sources}')
    else:
        print(f'Merged simple check: Success. All songs on merged playlists are present in sources: {source_tags}.')

    return counter_missing_from_sources


def merge(spotify, spotify_data, target_id, tags, exclude_tags, add_in_doubt=False):
    """
    Gets all songs from playlists with specific tags and add them to target playlist.
    Omits songs that are already there.
    Checks if there are similar songs (e.g. from single release).

    :param spotify:     spotipy object
    :param sources:     list of files with playlist ids
    :param target_id:   id of playlist where songs from sources will be added
    :param add_in_doubt:    True - adds songs even if song with similar name exists (e.g. same song from single)
    :return: None
    """
    logs_file_name = 'logs/merge.log'

    # Read all tracks from target
    target_playlist = []
    for playlist in spotify_data:
        if playlist['id'] == target_id:
            target_playlist = playlist
            break
    if len(target_playlist) < 1:
        print("BUG")
    
    target_ids = [track['track']['id'] for track in target_playlist['tracks']]

    #target_ids = [track['track']['id'] for track in target_track_list]
    #target_songs = [{'name': track['track']['name'], 'id': track['track']['id'], 'artist_id': track['track']['artists'][0]['id']} for track in target_track_list]
    counter_local_songs = 0
    counter_similar_songs = 0
    counter_added_songs = 0
    found_similar = False

    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        #for playlist in spotify_data:
        for i, playlist in enumerate(spotify_data):
            #print(f"\rMerge: merging playlist: {i + 1} / {len(spotify_data)}\t{playlist['name']}", end='')

            # Select playlists with any of tags and without exluded tags
            playlist_tags = shared_funcions.get_tags_from_playlist(playlist)
            tag_in_desc = any([tag in playlist_tags for tag in tags])
            if not tag_in_desc:     # If there is no tag in desc skip playlist
                continue
            exclude_tag_in_desc = any([tag in playlist_tags for tag in exclude_tags])
            if exclude_tag_in_desc:     # If there is no tag in desc skip playlist
                log_file.write(f"Skipping playlist:     {playlist['name']}\n")
                continue
            
            
            log_file.write(f"Adding songs form playlist:     {playlist['name']}\n")
            for track in playlist['tracks']:
                if track['track']['is_local']:
                    log_file.write(f"Local track            {track['track']['name']} from {playlist['name']} skipped.\n")        
                    continue

                track_id = track['track']['id']
                track_name = track['track']['name']
                artist_id = track['track']['artists'][0]['id']
                artist_name = track['track']['artists'][0]['name']
                found_similar = False

                if track_id in target_ids:
                    continue

                
                for song in target_playlist['tracks']:  # It can be done better
                    if song['track']['is_local']:
                        continue
                    if (track_name in song['track']['name'] or song['track']['name'] in track_name) and artist_id == song['track']['artists'][0]['id']:
                        found_similar = True
                        if add_in_doubt:
                            spotify.playlist_add_items(target_id, [track_id])
                            counter_added_songs += 1
                            with open(logs_file_name, "a", encoding='utf-8') as f:
                                log_file.write(f"Force add: {track_id} {artist_name} - {track_name} from {playlist['name']} added to {target_playlist['name']} despite that")
                                log_file.write(f"{song['track']['name']} by the same artist was already there.\n")
                        else:
                            with open(logs_file_name, "a", encoding='utf-8') as f:
                                log_file.write(f"Skipped:               {track_id} {artist_name} - {track_name} from {playlist['name']} not added to {target_playlist['name']} because ")
                                log_file.write(f"{song['track']['name']} by the same artist is already there.\n")
                        counter_similar_songs += 1
                        break

                if found_similar:
                    found_similar = False
                    continue

                spotify.playlist_add_items(target_id, [track_id])
                counter_added_songs += 1
                log_file.write(f"{track_id} {artist_name} - {track_name} from {playlist['name']} added to {target_playlist['name']}\n")

    print(f"Merge: {counter_added_songs} were added to {target_playlist['name']}; {counter_local_songs} local files from sources skipped.")
    if add_in_doubt and counter_similar_songs:
        print(f"Merge {target_playlist['name']}: {counter_similar_songs} songs with similar titles were also added to {target_playlist['name']}")
    else:
        print(f"Merge {target_playlist['name']}: {counter_similar_songs} songs with similar names were skipped.")
    print('')