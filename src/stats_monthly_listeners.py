import numpy as np
import matplotlib.pyplot as plt
from src import shared_funcions


def read_data(file):
    """
    Get all data from file.

    :param file: file path
    :return: dict {artists id: monthly listeners}
    """
    monthly_listeners = {}
    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue
            if line[0] == '#':
                continue
            line = line.split()
            monthly_listeners.update({line[0]: int(line[1])})

    return monthly_listeners


def search_name_by_value(artists, ml):
    return [artist['name'] for artist in artists if artist['monthly_listeners'] == ml][0]


def playlist_stats(artists, playlist_name):
    """


    :param artists: dict
    :param playlist_name:
    :return: None
    """
    monthly_listeners = [artist['monthly_listeners'] for artist in artists]

    min_monthly_listeners = min(monthly_listeners)
    max_monthly_listeners = max(monthly_listeners)
    mean_monthly_listeners = int(np.mean(monthly_listeners))
    median_monthly_listeners = int(np.median(monthly_listeners))

    min_x = int(np.floor(np.log10(min_monthly_listeners)))
    max_x = int(np.ceil(np.log10(max_monthly_listeners)))

    if max_x > 9:
        max_x = 9
    if min_x > 1:
        min_x -= 1
    xticks = np.arange(min_x, max_x + 2, 1)
    #labels = ['1 - 9', '10 - 99', '100 - 999', '1k - 9k', '10k - 99k', '100k - 999M', '1M - 9M', '10M - 99M', '>100M']
    labels = ['1', '10', '100', '1k', '10k', '100k', '1M', '10M', '100M', '1B']
    labels = labels[min_x:max_x + 2]

    stats = f'Min = {min_monthly_listeners:,} for {search_name_by_value(artists, min_monthly_listeners)}\n' \
            f'Max = {max_monthly_listeners:,} for {search_name_by_value(artists, max_monthly_listeners)}\n' \
            f'Mean = {mean_monthly_listeners:,}, Median = {median_monthly_listeners:,}'
    stats = stats.replace(',', ' ')

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ml = np.log10(monthly_listeners)
    ax.hist(ml, bins=xticks, label=stats, ec='black', histtype='bar', color='orange')  # - 0.56 to center ticks
    ax.set_title(f'"{playlist_name}" artist monthly listeners')
    ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('Monthly listeners')
    ax.set_ylabel('Number of artists')
    #ax.set_xlim(min_x - 0.5, max_x - 0.5)
    ax.set_xlim(min_x, max_x + 1)
    #ax.set_yscale('log')

    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=False)
    plt.legend()
    filename = 'stats/' + playlist_name + ' monthly listeners' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def make_stats(spotify, playlist_ids):
    """
    Make stats for all playlists.

    :param spotify: spotipy object
    :param playlist_ids: list of ids
    :return: None
    """
    plt.rcParams.update({'figure.max_open_warning': 0})

    data_file = 'data/montly_listeners_data.txt'
    all_monthly_listeners = read_data(data_file)

    for playlist_id in playlist_ids:
        artists = []
        artists_ids = []
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist
        print(f'Montly listeners stats: preparing stats for {playlist_name}')

        # Extract data only for artists from the playlist
        for track in track_list:
            if track['track']['is_local']:
                continue
            if track['track']['artists'][0]['id'] in artists_ids:
                continue

            id = track['track']['artists'][0]['id']
            name = track['track']['artists'][0]['name']
            if id not in all_monthly_listeners.keys():
                print(f'ERROR: Missing monthly listeners data for {id}\t{name}')
                continue

            if all_monthly_listeners[id] < 0:
                print(f'ERROR: Corrupted monthly listeners data for {id}\t{name}')
                continue

            artists.append({'id': id,
                            'name': name,
                            'monthly_listeners': int(all_monthly_listeners[id])
                          })
            artists_ids.append(id)

        playlist_stats(artists, playlist_name)
