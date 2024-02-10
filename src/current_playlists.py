import os
from src import shared_funcions


def check_ids(ids, all_playlists_file_path):
    """
    Check list of ids if all of them are still on my spotify (via checking file with dumped ids)
    """
    existing_playlist_ids = shared_funcions.read_sources([all_playlists_file_path])
    for playlist_id in ids:
        if playlist_id not in existing_playlist_ids:
            print(f'ERROR: {playlist_id} is no longer on Spotify.')
            return False

    print('Sources check: All ids are still valid.')
    return True


def get_playlists(spotify, all_playlists_file_path):
    """
    Gets all playlist ids from my spotify library and save them to file
    """
    with open(str(all_playlists_file_path), "w") as f:
        f.write('')
    response = spotify.user_playlists((spotify.me())['id'])
    print(f'Number of playlists on Spotify: {response["total"]}')

    playlists = response['items']
    while response['next']:
        response = spotify.next(response)
        playlists.extend(response['items'])

    for playlist in playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        with open(str(all_playlists_file_path), 'a', encoding='utf-8') as f:
            f.write(f'{playlist_id}\t{playlist_name}\n')
        #print(f'Playlist {playlist_name} has {playlist["tracks"]["total"]} tracks.')


def sanity_check(files, all_playlists_file_path):
    """
    Checks if all playlists listed in all_playlists file are listed in source files and vice versa
    files: List of files

    :param files:   list of manualy prepared files with playlist ids
    :param all_playlists_file_path:  file with downloaded current ids
    :return: True - every playlist is listed
    """

    names_sources, ids_sources = [], []
    passed_flag = True
    for file in files:
        if not os.path.isfile(file):
            print(f'ERROR: {file} does not exist. Skipping.')
            continue

        with open(str(file), "r", encoding='utf-8') as f:
            for line in f:
                if line == '\n' or line == ' ' or line == '\t':
                    continue
                line = line.split()
                id = line[0]
                name = line[1]
                for s in line[2:]:
                    name = name + ' ' + s
                if id in ids_sources:
                    print(f'ERROR: {name} is doubled in sources. Occurs in {file} and ')
                    passed_flag = False
                else:
                    ids_sources.append(id)
                    names_sources.append(name)

    if passed_flag:
        print('Sources check: No cross-sources duplicates')

    ids_main, names_main = [], []
    with open(str(all_playlists_file_path), "r", encoding='utf-8') as f:    # TODO: move to shared_functions
        for line in f:
            if line == '\n':
                continue
            line = line.split()
            id = line[0]
            name = line[1]
            for s in line[2:]:
                name = name + ' ' + s
            ids_main.append(id)
            names_main.append(name)

    if len(ids_sources) != len(ids_main):
        print(f'ERROR: Different number of playlists in sources and on spotify. {len(ids_sources)} / {len(ids_main)}')
        passed_flag = False

    missing_from_sources = (set(ids_main) - set(ids_sources))
    missing_from_main = (set(ids_sources) - set(ids_main))

    for id in missing_from_sources:
        print(f'{id}\t{names_main[ids_main.index(id)]} is missing from sources.')
    for id in missing_from_main:
        print(f'{id}\t{names_sources[ids_sources.index(id)]} is missing on {all_playlists_file_path}.')

    if missing_from_sources or missing_from_main:
        passed_flag = False
        print(f'ERROR: Playlists sources do not match current spotify status. Halting the script')
    else:
        print("Sources check: passed")

    return passed_flag
