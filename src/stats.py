import collections
import matplotlib.pyplot as plt
import numpy as np
import re
from src import shared_funcions

'''
Avalible stats:
Number of songs   / first letter of title
Number of artists / first letter of name
Number of songs   / release year
Number of songs   / song duration
Number of artists / Number of artists songs
Number of different artists in first n songs on playlist
Most popular words in song title
Most popular words in song lyrics
'''


def years(songs, playlist_name):
    """
    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """
    years = [song['year'] for song in songs]

    start_year = min(years) - 1
    start_year = start_year - (start_year % 5)
    end_year = 2025

    fig, ax = plt.subplots()
    ax.hist(years, bins=np.arange(start_year, end_year), ec='black', histtype='bar', color='orange')
    ax.set_title(f'"{playlist_name}" release year')
    ax.set_xlim([start_year, end_year])
    ax.set_xticks(np.arange(start_year, end_year, 5))
    ax.set_xlabel('Years')
    ax.set_ylabel('Number of songs')
    ax.tick_params(axis='x', which='minor', bottom=False)
    plt.minorticks_on()

    filename = 'stats/' + playlist_name + ' years.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def duration(songs, playlist_name):
    """
    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """
    times = [song['duration'] for song in songs]

    min_s = 0
    max_s = max(times) + 1
    max_s = max_s - (max_s % 60) + 61  # rounding

    xticks = np.arange(min_s, max_s, 20)
    labels = np.where(xticks % 60 == 0, (xticks / 60).astype(int), '')
    fig, ax = plt.subplots()
    ax.hist(times, bins=np.arange(min_s, max_s, 20), ec='black', histtype='bar', color='orange')
    ax.set_title(f'"{playlist_name}" song duration [min]')
    ax.set_xlim([min_s, max_s])
    ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('Duration [min]')
    ax.set_ylabel('Number of songs')
    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=False)

    filename = 'stats/' + playlist_name + ' duration.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def mean_duration_per_year(songs, playlist_name):
    """
    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """
    years = np.array([song['year'] for song in songs])

    start_year = min(years) - 1
    end_year = 2025
    start_year = start_year - (start_year % 5)

    total_duration = np.zeros((end_year - start_year + 1))
    no_of_songs = np.zeros((end_year - start_year + 1))
    years = years - start_year
    for i in range(len(songs)):
        total_duration[years[i]] += songs[i]['duration']
        no_of_songs[years[i]] += 1

    mean = []   # eeee?
    for i in range(len(no_of_songs)):
        if no_of_songs[i] > 0:
            mean.append(total_duration[i] / no_of_songs[i] / 60)
        else:
            mean.append(0)
    #mean = np.where(no_of_songs > 0, total_duration / no_of_songs / 60, 0)

    fig, ax = plt.subplots()
    ax.bar(np.arange(start_year, end_year + 1) + 0.5, mean, color='orange', width=1, edgecolor='black')
    ax.set_title(f'"{playlist_name}" duration per year')
    ax.set_xlim([start_year, end_year])
    ax.set_xticks(np.arange(start_year, end_year, 5))
    ax.set_xlabel('Years')
    ax.set_ylabel('Mean song duration [min]')
    plt.minorticks_on()

    filename = 'stats/' + playlist_name + ' mean duration per year.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def songs_per_band(songs, playlist_name):
    """
    Slightly misleading name.
    Makes histogram with number of artists having n number of songs

    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """

    artists = np.unique([song['artist_name'] for song in songs])    # Why didn't I use set() ?
    no_of_songs = np.zeros(len(artists))
    for song in songs:
        for i in range(len(artists)):
            if artists[i] == song['artist_name']:
                no_of_songs[i] += 1

    min_s = 0
    max_s = max(no_of_songs) + 2
    xticks = np.arange(min_s, max_s, 1)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(no_of_songs, bins=xticks - 0.5, ec='black', histtype='bar', color='orange')  # - 0.56 to center ticks
    ax.set_title(f'"{playlist_name}" number of artists per number of their songs')
    ax.set_xlabel('Number of songs')
    ax.set_ylabel('Number of artists')
    ax.set_xlim([0.1, max_s])
    plt.minorticks_on()
    filename = 'stats/' + playlist_name + ' songs per artists' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def first_letter_of_titles(songs, playlist_name):
    """
    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """
    first_letters = ''
    for song in songs:
        title = song['name']
        title = re.sub('A ', '', title)
        title = re.sub('An ', '', title)
        title = re.sub('The ', '', title)
        first_letters += title[0]
    first_letters = first_letters.upper()
    chars = [ord(c) for c in first_letters]

    latin = [c for c in chars if 65 <= c <= 90]  # [65-90] ]uppercase latin   #[97-122] - lowercase
    digits = [c for c in chars if 48 <= c <= 57]
    other = len(first_letters) - len(latin) - len(digits)

    letters = latin
    for d in range(len(digits)):
        letters.append(91)
    for d in range(other):
        letters.append(92)

    xticks = np.arange(65, 94, 1)
    labels = [chr(x) for x in xticks]
    labels[-3] = '%d'
    labels[-2] = '%c'
    labels[-1] = ''
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(letters, bins=xticks - 0.5, ec='black', histtype='bar', color='orange')  # - 0.5 to center ticks
    ax.set_title(f'"{playlist_name}" song title first letters')
    ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('First character')
    ax.set_ylabel('Number of songs')
    ax.set_xlim([64.2, 92.8])
    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=False)
    filename = 'stats/' + playlist_name + ' first character song title' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def first_letter_of_artist(songs, playlist_name):
    """
    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """

    first_letters = ''
    for song in songs:
        title = song['artist_name']
        title = re.sub('A ', '', title)
        title = re.sub('An ', '', title)
        title = re.sub('The ', '', title)
        first_letters += title[0]
    first_letters = first_letters.upper()
    chars = [ord(c) for c in first_letters]

    latin = [c for c in chars if 65 <= c <= 90]  # [65-90] ]uppercase latin   #[97-122] - lowercase
    digits = [c for c in chars if 48 <= c <= 57]
    other = len(first_letters) - len(latin) - len(digits)

    letters = latin
    for d in range(len(digits)):
        letters.append(91)
    for d in range(other):
        letters.append(92)

    xticks = np.arange(65, 94, 1)
    labels = [chr(x) for x in xticks]
    labels[-3] = '%d'
    labels[-2] = '%c'
    labels[-1] = ''
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(letters, bins=xticks - 0.5, ec='black', histtype='bar', color='orange')  # - 0.56 to center ticks
    ax.set_title(f'"{playlist_name}" artist name first letters')
    ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('First character')
    ax.set_ylabel('Number of songs')
    ax.set_xlim([64.2, 92.8])
    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=False)
    filename = 'stats/' + playlist_name + ' first character artist' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def most_common_word_in_titles(songs, playlist_name):
    """
    Makes text file with most common words in titles

    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """

    words = []
    stop_words = ['a', 'an', 'the', 'of', '&', '/']
    stop_words.extend(['in', 'with', 'and', 'you', 'i', 'no', 'to', 'for', 'your', 'on', 'me', 'we', 'out', 'it', 'have', 'are', 'am', 'be', 'is', 'be', 'or', 'up', 'by', 'na', 'my', 'do', 'don\'t'])
    stop_words.extend(['metal', 'cover'])
    max_to_show = 50
    filename = 'stats/' + playlist_name + ' most common words in titles.txt'

    for song in songs:
        title = song['name'].lower()

        title = re.sub('-.*', '', title)        # Removes ' - Remastered' and similar things from title
        title = re.sub('[fF]eat.*', '', title)
        title = re.sub('\'s', '', title)
        title = re.sub('[,\[\](){}]', '', title)

        words.extend(title.split())

    words = [word.capitalize() for word in words if word not in stop_words]   # Skip stop words
    most_common_words = collections.Counter(words).most_common(max_to_show)   # no need to check if max_to_show is greater than len of dict

    with open(filename, 'w', encoding="utf-8") as f:
        f.write(f'Skipped words: ')
        for word in stop_words:
            f.write(f'{word}, ')
        f.write('\n\n')

        for word, occurances in most_common_words:
            f.write(f'{word}\t\t{occurances}\n')


def most_common_word_in_lyrics(songs, playlist_name):
    """
    Makes text file with most common words in lyrics

    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :return: None
    """

    words = []
    stop_words = ['a', 'an', 'the', 'of', '&', '/']
    stop_words.extend(['in', 'with', 'and', 'you', 'i', 'no', 'to', 'for', 'your', 'on', 'me', 'we', 'out', 'it', 'have', 'are', 'am', 'be', 'is', 'be', 'or', 'up', 'by', 'na', 'my', 'do', 'don\'t'])
    stop_words.extend(['i\'m', 'will', 'like', 'all', 'that', 'this', 'but', 'what', 'our', 'when', 'so', 'also', 'it\'s', 'not', 'they', 'just', 'their', 'as', 'time', 'life', 'way', 'can', 'oh', 'da'])
    stop_words.extend(['You\'re', 'Can\'t', 'I\'ve', 'At', 'Was', 'We\'re', 'I\'ll', ])
    max_to_show = 50
    filename = 'stats/' + playlist_name + ' most common words in lyrics.txt'

    song_ids = [song['id'] for song in songs]
    all_lyrics = shared_funcions.read_lyrics(song_ids)  # Get lyrics from file
    if not all_lyrics:
        return None

    for lyrics in all_lyrics:
        lyrics = lyrics.lower()

        lyrics = re.sub('\n', ' ', lyrics)

        words.extend(lyrics.split())

    words = [word.capitalize() for word in words if word not in stop_words]  # Skip stop words
    most_common_words = collections.Counter(words).most_common(max_to_show)  # no need to check if max_to_show is greater than len of dict

    with open(filename, 'w', encoding="utf-8") as f:
        f.write(f'Skipped words: ')
        for word in stop_words:
            f.write(f'{word}, ')
        f.write('\n\n')

        for word, occurances in most_common_words:
            f.write(f'{word}\t\t{occurances}\n')


def artists_in_first_n_songs(songs, playlist_name, shuffle=False):
    """
    Makes graph of how many different artists occupy first n positions in playlist

    :param songs: dict containing songs data
    :param playlist_name: name of analysed playlist
    :param shuffle: True - shuffle artists positions. False - keep playlist
    :return: None
    """
    artist_names = [song['artist_name'] for song in songs]
    if shuffle:
        np.random.shuffle(songs)

    no_of_artists = np.zeros(len(artist_names))
    for i in range(0, len(artist_names)):
        no_of_artists[i] = len(np.unique(artist_names[:i+1]))

    min_s = 0
    max_s = len(no_of_artists) + 1
    x = np.arange(0, len(no_of_artists))
    xticks = np.arange(min_s, max_s, 1)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.scatter(x, no_of_artists, label=f'{playlist_name}', s=4, c='blue')
    ax.set_title(f'"{playlist_name}" number of different artists in first x songs')
    #ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('Number of songs')
    ax.set_ylabel('Number of artists')
    ax.set_xlim([0, max_s])
    ax.set_ylim([0, np.max(no_of_artists) + 1])
    plt.minorticks_on()
    filename = 'stats/' + playlist_name + ' different artists in x songs' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def artists_in_first_n_songs_compare(spotify, playlist_id_1, playlist_id_2, shuffle=False, fit=False):
    """
    Similar to artists_in_first_n_songs but makes plot for two playlists on one figure.
    """
    track_list_1, playlist_name_1 = shared_funcions.get_track_list(spotify, playlist_id_1)  # Get all tracks from playlist
    track_list_2, playlist_name_2 = shared_funcions.get_track_list(spotify, playlist_id_2)  # Get all tracks from playlist

    artist_names_1 = [track['track']['artists'][0]['name'] for track in track_list_1 if not track['track']['is_local']]
    artist_names_2 = [track['track']['artists'][0]['name'] for track in track_list_2 if not track['track']['is_local']]

    if shuffle:
        np.random.shuffle(artist_names_1)
        np.random.shuffle(artist_names_2)

    no_of_artists_1 = np.zeros(len(artist_names_1))
    for i in range(0, len(artist_names_1)):
        no_of_artists_1[i] = len(np.unique(artist_names_1[:i+1]))

    no_of_artists_2 = np.zeros(len(artist_names_2))
    for i in range(0, len(artist_names_2)):
        no_of_artists_2[i] = len(np.unique(artist_names_2[:i + 1]))

    min_s = 0
    max_s = max(len(no_of_artists_1) + 1, len(no_of_artists_2) + 1)
    x = np.arange(0, max_s)
    xticks = np.arange(min_s, max_s, 1)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.scatter(x[:len(no_of_artists_1)], no_of_artists_1, label=f'{playlist_name_1}', s=4, c='blue')
    ax.scatter(x[:len(no_of_artists_2)], no_of_artists_2, label=f'{playlist_name_2}', s=4, c='red')
    ax.set_title(f'"{playlist_name_1}" vs "{playlist_name_2}": Number of different artists in first x songs')
    # ax.set_xticks(xticks, labels=labels)
    ax.set_xlabel('Number of songs')
    ax.set_ylabel('Number of artists')
    ax.set_xlim([0, max_s])
    ax.set_ylim([0, max(np.max(no_of_artists_1) + 1, np.max(no_of_artists_2) + 1)])
    plt.minorticks_on()
    plt.legend()

    if fit:
        import scipy

        def fit_fun(x, n, a):
            return n * np.power(x, a)

        params_1 = scipy.optimize.curve_fit(fit_fun, x[:len(no_of_artists_1)], no_of_artists_1)[0]
        params_2 = scipy.optimize.curve_fit(fit_fun, x[:len(no_of_artists_2)], no_of_artists_2)[0]
        #params_2 = scipy.optimize.curve_fit(fit_fun, x[:len(no_of_artists_2)], no_of_artists_2, p0=[5.1, 0.53], bounds=([0.1, 0.1], [10, 1]))[0]
        y_1 = fit_fun(x, *params_1)
        y_2 = fit_fun(x, *params_2)

        plt.plot(x[:len(y_1)], y_1, c='cyan')
        plt.plot(x[:len(y_2)], y_2, c='orange')
    filename = 'stats/' + 'xcompare ' + playlist_name_1 + ' vs ' + playlist_name_2 + ' different artists in x songs' + '.png'
    plt.savefig(filename, dpi=300)
    plt.cla()


def make_all_stats(spotify, playlist_ids):
    """
    Make all avalible stats for a playlist.

    :param spotify:       spotipy object
    :param playlist_ids:  list of playlists ids to make stats
    :return: None
    """

    plt.rcParams.update({'figure.max_open_warning': 0})
    for playlist_id in playlist_ids:
        songs = []
        track_list, playlist_name = shared_funcions.get_track_list(spotify, playlist_id)  # Get all tracks from playlist

        print(f'Stats: preparing stats for {playlist_name}')

        # Prepare dict with data of songs from a playlist
        for track in track_list:
            if track['track']['is_local']:
                continue

            songs.append({'id': track['track']['id'],
                          'name': track['track']['name'],
                          'artist_id': track['track']['artists'][0]['id'],
                          'artist_name': track['track']['artists'][0]['name'],
                          #'album_type': track['track']['album']['album_type'],
                          'year': int(track['track']['album']['release_date'][:4]),  # get release year
                          'duration': int(track['track']['duration_ms'] / 1000)  # in s
                          })

        years(songs, playlist_name)
        duration(songs, playlist_name)
        first_letter_of_titles(songs, playlist_name)
        first_letter_of_artist(songs, playlist_name)
        songs_per_band(songs, playlist_name)
        mean_duration_per_year(songs, playlist_name)
        artists_in_first_n_songs(songs, playlist_name)
        most_common_word_in_titles(songs, playlist_name)
        most_common_word_in_lyrics(songs, playlist_name)
