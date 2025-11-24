import pickle
from src import shared_funcions
from src import stats
import re


def print_playlist(spotify, playlist_id):
    tracks, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)
    for i, track in enumerate(tracks):
        if track['track'] is None:
            print(track, '\n')
            continue

        track_id = track['track']['id']
        track_name = track['track']['name']
        artist_id = track['track']['artists'][0]['id']
        artist_name = track['track']['artists'][0]['name']

        name_len = 45
        #track_name = f'{artist_name} - {track_name}' + ' ' * name_len
        #track_name = track_name[:name_len]
        print(f"{artist_name}\t{track_name}")


def log_artists_song_no(spotify, playlist_id, thr=5):
    tracks, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)
    artists = {}
    for i, track in enumerate(tracks):
        if track['track'] is None:
            print(track, '\n')
            continue

        track_id = track['track']['id']
        track_name = track['track']['name']
        artist_id = track['track']['artists'][0]['id']
        artist_name = track['track']['artists'][0]['name']

        if artist_name == '':
            #print(track_name)
            continue

        if artist_id not in artists:
            artists[artist_id] = {"name": artist_name, "tracks": [track]}
        else:
            artists[artist_id]["tracks"].append(track)

    logs_file_name = 'logs/artists_number_of_songs.log'
    artists = dict(sorted(artists.items(), key=lambda art: art[1]['name']))
    with open(logs_file_name, "w", encoding='utf-8') as f:
        f.write(f"Artists with > {thr} songs on {playlist_name}\n")
        for artist in artists:
            name_len = 25
            if len(artists[artist]["tracks"]) >= thr:
                text = f'{artists[artist]["name"]}' + ' ' * (max(0, name_len - len(artists[artist]["name"]))) + '\t' + str(len(artists[artist]["tracks"])) + '\n'
                f.write(text)
            #text = word[0] + (16 - len(word[0])) * ' ' + '\t' + str(word[1])
            #f.write(text + '\n')

        name_len = 45
        #track_name = f'{artist_name} - {track_name}' + ' ' * name_len
        #track_name = track_name[:name_len]
        #print(f"{artist_name}\t{track_name}")


def remove_dupes_within_playlists(spotify, playlist_id, renew_data=False):
    data_filename = 'data/dedup_temp.pkl'
    if renew_data:
        tracks, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)
        with open(data_filename, 'wb') as f:
            pickle.dump([tracks, playlist_name], f)
    else:
        with open(data_filename, 'rb') as f:
            tracks, playlist_name = pickle.load(f)

    exceptions = [None, '5zA8vzDGqPl2AzZkEYQGKh','1B75hgRqe7A4fwee3g3Wmu','4cOdK2wGLETKBW3PvgPWqT', '5rJbinKaTDLKoGnSxPuzQr','14F0W8JdM5DKgggLI2ILDH','0c6TYdegl51Zat3ih5ziB7','3EXNSIvni9q4Osg4xrth7o','1AdpIvjKMhp3tNSHVNBzgy','5PsUB0ISfQxRLhF5DmI5Ks','694T7sMv0bFvPbMMXvZlyj','2k6dU3c2IBotzynOyevHJx','7IVZmy1CDi1SRMxD4h3mzX','6XSlYoyCBsBFIgvD4Gz04m','17FBAPRaDeIGL5Ou3tS4OO','4o8C59MLyVP6qwKrzW8Avr','3ZZq9396zv8pcn5GYVhxUi','6urCAbunOQI4bLhmGpX7iS']
    to_remove_ids = []
    songs = []
    logs_file_name = 'logs/mieszkan_dedup.log'
    counter_duplicates = counter_local = 0

    print(f"Deduping: {playlist_name}")
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')
        for i, track in enumerate(tracks):
            print(f'\rDedup progress: {i + 1} / {len(tracks)}; Dupes: {counter_duplicates}', end='')
            if track['track'] is None:
                print(track, '\n')
                continue

            if track['track']['is_local']:
                counter_local = counter_local + 1
                #log_file.write(f"Local song: {track['track']['name']}\n")
                continue

            if track['track']['id'] in exceptions:
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            name_len = 45
            track_name = f'{artist_name} - {track_name}' + ' ' * name_len
            track_name = track_name[:name_len]

            if track['track']['is_local']:
                counter_local = counter_local + 1
                #log_file.write(f"Local song: {track['track']['name']}\n")
                continue

            for song in songs:
                if track['track']['id'] == song['track']['id']:
                    track_name = f"{track['track']['artists'][0]['name']} - {track['track']['name']}{' ' * name_len}"[:name_len]
                    song_name = f"{song['track']['artists'][0]['name']} - {song['track']['name']}{' ' * name_len}"[:name_len]
                    log_file.write(f"{track_name}\t/\t{song_name} \tID dupe\t\t{track['track']['id']} {song['track']['id']}\n")
                    counter_duplicates = counter_duplicates + 1
                    # Dont remove that, asl remove all will kill playlist
                    continue
                track_name = track['track']['name']
                track_name = track['track']['name'].lower()
                track_name = re.sub(' ', '', track_name)
                song_name = song['track']['name']
                song_name = song['track']['name'].lower()
                song_name = re.sub(' ', '', song_name)
                if track_name == song_name and (track['track']['artists'][0]['name'] == song['track']['artists'][0]['name']):
                #if (track_name in song_name or song_name in track_name) and (track['track']['name'] == song['track']['name']):
                    counter_duplicates = counter_duplicates + 1
                    name = f"{track['track']['artists'][0]['name']} - {track['track']['name']}{' ' * name_len}"[:name_len]
                    song_name = f"{song['track']['artists'][0]['name']} - {song['track']['name']}{' ' * name_len}"[:name_len]
                    log_file.write(f"{name}\t/\t{song_name} \tName match\t\t{track['track']['id']} {song['track']['id']}\n")
                    if song['track']['id'] is not None:
                        to_remove_ids.append(track['track']['id'])

            songs.append(track)


        print(f"\n")
        if counter_duplicates:
            print(f'Number of duplicated songs found: {counter_duplicates}')
        else:
            print(f'No duplicated songs found.')
        print(f"Removing {len(to_remove_ids)} songs")
        print(f'Number of local songs found: {counter_local}')

        log_file.write(f"Removing {len(to_remove_ids)} songs\n")
        for i, track_id in enumerate(to_remove_ids):
            log_file.write(f"{track_id}\n")
            # spotify.playlist_remove_all_occurrences_of_items(playlist_id, [track['track']['id']])


def sync_mieszkan(spotify, main_playlist_id='0deUpgRxeiONMtk055LcoK', target_playlist_id='1WvfRAyARbMgvpSkdTPtQe', renew_data=True, remove_or_log_flag=True):
    #main - mieszkan wspanialy - '0deUpgRxeiONMtk055LcoK'
    #main - mieszkan wspanialy backup- '1WvfRAyARbMgvpSkdTPtQe'
    data_filename = 'data/sync_maly_mieszkan_temp.pkl'
    if renew_data:
        print("Getting data for main playlist")
        main_tracks, main_playlist_name = shared_funcions.get_track_list(spotify, main_playlist_id)
        print("Getting data for target")
        target_tracks, target_playlist_name = shared_funcions.get_track_list(spotify, target_playlist_id)
        with open(data_filename, 'wb') as f:
            pickle.dump([target_tracks, target_playlist_name, main_tracks, main_playlist_name], f)
    else:
        with open(data_filename, 'rb') as f:
            target_tracks, target_playlist_name, main_tracks, main_playlist_name = pickle.load(f)

    to_remove_ids = []
    logs_file_name = 'logs/mieszkan_sync.log'

    print(f"len main: {len(main_tracks)}; len target: {len(target_tracks)}")
    print(f"name main: {main_playlist_name}; name target: {target_playlist_name}")
    main_ids = [track['track']['id'] for track in main_tracks if not track['track']['is_local']]

    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')
        for i, track in enumerate(target_tracks):
            if track['track'] is None:
                print("CRITICAL BUG: ")
                print(track, '\n')
                continue

            if track['track']['is_local']:
                continue

            if track['track']['id'] not in main_ids:
                log_file.write(f"{track['track']['artists'][0]['name']} - {track['track']['name']}\t\t will be removed\n")
                to_remove_ids.append(track['track']['id'])

        log_file.write(f"Removing {len(to_remove_ids)} songs from {target_playlist_name}\n")
        print(f"Removing {len(to_remove_ids)} songs from {target_playlist_name}\n")
        if remove_or_log_flag:
            for i, track_id in enumerate(to_remove_ids):
                spotify.playlist_remove_all_occurrences_of_items(target_playlist_id, [track_id])


def remove_dupes_within_playlists_backup(spotify, playlist_id, renew_data=False):
    data_filename = 'data/dedup_temp.pkl'
    if renew_data:
        tracks, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)
        with open(data_filename, 'wb') as f:
            pickle.dump([tracks, playlist_name], f)
    else:
        with open(data_filename, 'rb') as f:
            tracks, playlist_name = pickle.load(f)

    exceptions = []
    to_remove_ids = []
    logs_file_name = 'logs/mieszkan_dedup.log'
    counter_duplicates = counter_local = 0

    print(f"Deduping: {playlist_name}")
    with open(logs_file_name, "w", encoding='utf-8') as log_file:
        log_file.write('')
        for i, track in enumerate(tracks):
            print(f'\rDedup progress: {i + 1} / {len(tracks)}; Dupes: {counter_duplicates}', end='')
            if track['track'] is None:
                print(track, '\n')
                continue

            track_id = track['track']['id']
            track_name = track['track']['name']
            artist_id = track['track']['artists'][0]['id']
            artist_name = track['track']['artists'][0]['name']

            name_len = 45
            track_name = f'{artist_name} - {track_name}' + ' ' * name_len
            track_name = track_name[:name_len]

            if track['track']['is_local']:
                counter_local = counter_local + 1
                #log_file.write(f"Local song: {track['track']['name']}\n")

            for other_track in tracks:
                if other_track['track']['id'] in exceptions:
                    continue

                if other_track['track']['is_local']:
                    continue

                if track['track']['id'] == other_track['track']['id']:
                    continue

                #if track['track']['artists'][0]['name'] == other_track['track']['artists'][0]['name'] and (track['track']['name'] in other_track['track']['name'] or other_track['track']['name'] in track['track']['name']):
                if track['track']['artists'][0]['name'] == other_track['track']['artists'][0]['name'] and (track['track']['name'] == other_track['track']['name']):
                    counter_duplicates = counter_duplicates + 1
                    name = f"{track['track']['artists'][0]['name']} - {track['track']['name']}{' ' * name_len}"[:name_len]
                    other_track_name = f"{other_track['track']['artists'][0]['name']} - {other_track['track']['name']}{' ' * name_len}"[:name_len]
                    log_file.write(f"{track['track']['id']} {other_track['track']['id']} - {name}\t/\t{other_track_name}\n")
                    if track['track']['id'] is not None:
                        exceptions.append(track['track']['id'])
                    if other_track['track']['id'] is not None:
                        to_remove_ids.append(other_track['track']['id'])

        print(f"\n")
        if counter_duplicates:
            print(f'Number of duplicated songs found: {counter_duplicates}')
        else:
            print(f'No duplicated songs found.')
        print(f"Removing {len(to_remove_ids)} songs")
        print(f'Number of local songs found: {counter_local}')

        log_file.write(f"Removing {len(to_remove_ids)} songs")
        for i, track_id in enumerate(to_remove_ids):
            log_file.write(f"{track_id}\n")
            # spotify.playlist_remove_all_occurrences_of_items(playlist_id, [track['track']['id']])


def random_mieszkan_stats(spotify):

    #pl_wszysciutenko_id = '5ILM7FGO30AanFwmfuLXVB'
    mieszkan_wspanialy = '0deUpgRxeiONMtk055LcoK'
    mieszkan_wspanialy_b = '3paHJWCisOUGbIgdBR1jGq'
    top_of_the_top_u = '0k5DCITU0LEZZkgul7Ey5M'
    top_adam = '6MBd4UoRtoeoe8shYu2ioj'
    top_pio = '4Q5z9tpuyoIlXvNeSkV3A3'
    allar_ja = '6UTHiiydwvjK1NZ7mZ7u7O'
    allar_tocz = '4r1Rn6d6ZPYSeEatSefOOu'

    stats.make_all_stats_data_based(spotify, top_adam, renew_data=True)
    stats.make_all_stats_data_based(spotify, top_pio, renew_data=True)
    stats.artists_in_first_n_songs_compare(spotify, top_of_the_top_u, top_pio)

    
    pass
    #pl_allar_id = '6UTHiiydwvjK1NZ7mZ7u7O'
    #pl_wszysciutenko_id = '5ILM7FGO30AanFwmfuLXVB'
    #mieszkan wspanialy = '0deUpgRxeiONMtk055LcoK'
    #top_of_the_top_u = '0k5DCITU0LEZZkgul7Ey5M'
    #top_adam = '6MBd4UoRtoeoe8shYu2ioj'
    #top_pio = '4Q5z9tpuyoIlXvNeSkV3A3'