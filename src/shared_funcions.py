import os


def read_sources(sources):
    """
    Reads all listed files and returns list of playlist ids
    :param sources: List of file paths
    :return: List of playlist ids
    """
    playlist_ids = []
    for file in sources:
        if not os.path.isfile(file):
            continue

        with open(str(file), "r", encoding='utf-8') as f:
            for line in f:
                if line == '\n':
                    continue

                if line[0] == '#':
                    continue

                line = line.split()
                playlist_ids.append(line[0])

    return playlist_ids


def read_basic_exceptions(file):
    """
    Getting only ids of allowed exceptions
    :param file: exception file path
    :return: list of song ids
    """
    exceptions = []
    if not os.path.isfile(file):
        return exceptions

    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue

            if line[0] == '#':
                continue

            line = line.split()
            exceptions.append(line[0])

    return exceptions


def read_exceptions_with_playlist(file):
    """
    Getting id of allowed exceptions with id of playlist where exeption is accepted.
    :param file: exception file path
    :return: List of tuples containing song_id and playlist_id
    """
    exceptions = []
    if not os.path.isfile(file):
        return exceptions

    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue

            if line[0] == '#':
                continue

            line = line.split()
            exceptions.append((line[0], line[1]))

    return exceptions


def read_lyrics(song_ids, file='data/lyrics.txt'):
    """
    Reads lyrics file and returns list of lyrics only for specific songs
    Note: lyrics file format:
    # {id}
    {artist} - {title}
    \n
    {lyrics}
    \n
    """
    song_id = ''
    lyrics = ''
    data = []

    if not os.path.isfile(file):
        return data

    skip = False
    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line[0] == '#':
                if song_id in song_ids:
                    data.append(lyrics)
                song_id = line.split()[1]
                lyrics = ''
                skip = True  # brutal way to skip next line
                continue

            if skip:
                skip = False
                continue

            if line == '\n':
                continue

            lyrics = lyrics + line
            pass

    return data


def get_track_list(spotify, playlist_id):
    """
    Get all tracks from playlist
    """
    response = spotify.playlist(playlist_id)
    playlist_name = response['name']
    track_list = response['tracks']['items']
    response = response['tracks']
    while response['next']:
        response = spotify.next(response)
        track_list.extend(response['items'])

    return track_list, playlist_name
