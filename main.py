import sys, pickle
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_CLIENT_URL, SCOPE_MASTER

from src import tags
from src import single_finder
from src import duplicates_finder
from src import merge
from src import lyrics
from src import stats
from src import specific_workflows
"""
Features modifying Spotify:


Other features save results to .log files, so all found cases(single, duplicate etc.) needs to be removed manually.

Removed: 
Get_genres_for_playlist
ARTIST EXPLORER - Spotify depreaceted API for that. TODO: Move to last.fm API

TODO Duplicate songs make better legs for copy poaste to exceptions
TODO: Duplicate artists Make excemptions based on specific songs not artists.

    Check_id currently can check only ids from my spotify. Find better way to check any playlist id
    Fill parameters in function comments
    Exceptions have hardcoded file names. Move filenames to variables in case of update
    Fix printing playlist name in download lyrics 
    Fix printing playlist name in sources check
    
    Utilities:
    Making playlist with every song added to sources in last 6 months?
    Making playlist with every song of specific artist
"""


def workflow(spotify):
    pass
    #TODO:
    #Make data
    #Check tags
    #Find singles
    #Find duplicates on sources artists
    #Find duplicates on sources songs
    #Check merged

    # Merge to Allar
    # Merge to wszysciutenko
    # Merge to All met
    # Merge to Allhamama

    # Renew local data
    # Check merged
    # Get lyrics
    # Make stats


def standard_workflow(spotify, merge_flag=False, renew_data=False, renew_lyrics=True):
    tag_data = tags.tag_data        # ???
    
    data_filename = 'data/spotify_data.pkl'

    '''
    Get all user's playlists to spotify_data dict
    '''
    if renew_data:
        spotify_data = tags.get_playlist_data(spotify)
        with open(data_filename, 'wb') as f:
            pickle.dump(spotify_data, f)
    else:
        with open(data_filename, 'rb') as f:
            spotify_data = pickle.load(f)
    #print(f'Number of playlists on Spotify: {len(spotify_data)}')


    '''
    Check if all playlists have tags
    '''
    #   spotify_data[0]['description'] = ''     #Debug check
    flag_missing_tags = tags.check_if_tags_exist(spotify_data)
    tags.save_tags_to_logs(spotify_data)
    if flag_missing_tags:
        raise Exception("Some playlists are missing Tags. Check logs/tags.log")

    '''
    Find songs from single release or EP, but they shoud be removed manually or marked as exceptions
    Found singles are listed in log file
    '''
    single_finder.find_singles(spotify_data, ['S'])
    print('')

    ''' 
    Finding songs that occur on two different playlists on sources. There should be no such songs
    Finding artists that populate more than one playlists. Exceptions are based on specific song
    '''
    #duplicates_finder.find_duplicaded_songs(spotify_data, ['S'], use_exceptions=False)
    duplicates_finder.find_duplicaded_songs(spotify_data, ['S', 'P'], ['BUG'], use_exceptions=True)

    duplicates_finder.find_duplicated_artists(spotify_data, ['S'], ['BUG'], use_exceptions=True)
    #duplicates_finder.find_duplicated_artists(spotify_data, ['S', 'P'], use_exceptions=True)

    #duplicates_finder.check_for_similar_names(spotify_data, ['S'], use_exceptions=True)
    print('')

    '''
    Check if all songs on merged playlists are on sources
    '''
    merge.check_merged(spotify_data, ['M'], ['S'])
    merge.check_merged(spotify_data, ['M'], ['S', 'P'])
    print('')

    '''
    Merge all songs from playlists 
    '''
    pl_allar_id = '6UTHiiydwvjK1NZ7mZ7u7O'
    pl_wszysciutenko_id = '5ILM7FGO30AanFwmfuLXVB'
    pl_top_of_the_top_u = '0k5DCITU0LEZZkgul7Ey5M'
    pl_mieszkan_wspanialy = '0deUpgRxeiONMtk055LcoK'
    pl_mieszkan_wspanialy_b = '3paHJWCisOUGbIgdBR1jGq'
    pl_allamham_id = '5OTAUUzEG5B9iMAsLD6W4X'
    pl_allmet_id = '0r7wjUxEpKznRpsLLonaKo'
    pl_pojebance_id = '2TBgpwmYJjJw905nI7coWP'
    #merge.merge(spotify, spotify_data, pl_mieszkan_wspolny, tags=['S'], exclude_tags=[], add_in_doubt=False)
    #return None

    if merge_flag:
        merge.merge(spotify, spotify_data, pl_allar_id, tags=['S'], exclude_tags=['nieAR', 'PL', 'D', 'BUG'], add_in_doubt=True)
        merge.merge(spotify, spotify_data, pl_allamham_id, tags=['MD'], exclude_tags=['nieAR', 'PL', 'D', 'BUG'], add_in_doubt=False)
        merge.merge(spotify, spotify_data, pl_allmet_id, tags=['MD', 'VH'], exclude_tags=['nieAR', 'PL', 'D', 'BUG'], add_in_doubt=False)
        merge.merge(spotify, spotify_data, pl_pojebance_id, tags=['D'], exclude_tags=[], add_in_doubt=False)
        merge.merge(spotify, spotify_data, pl_wszysciutenko_id, tags=['S'], exclude_tags=[], add_in_doubt=False)

    '''
    Download lyrics for all songs on all playlists with 'S' tag
    '''
    if renew_lyrics:
        lyrics.get_lyrics(spotify_data, ['S'], check_existing_file=True, preserve_logs=False)

    stats.make_all_stats(spotify_data, pl_top_of_the_top_u)
    stats.make_all_stats(spotify_data, pl_allar_id)
    stats.make_all_stats(spotify_data, pl_allmet_id)
    stats.make_all_stats(spotify_data, pl_wszysciutenko_id)
    stats.make_all_stats(spotify_data, pl_mieszkan_wspanialy)
    stats.make_all_stats(spotify_data, pl_mieszkan_wspanialy_b)


if __name__ == '__main__':
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                                        redirect_uri=SPOTIPY_CLIENT_URL,
                                                        scope=SCOPE_MASTER))

    #test_workflow(spotify, merge_flag=False, renew_data=True)

    standard_workflow(spotify, merge_flag=False, renew_data=False, renew_lyrics=True)

    #pl_allar_id = '6UTHiiydwvjK1NZ7mZ7u7O'
    #pl_wszysciutenko_id = '5ILM7FGO30AanFwmfuLXVB'
    #mieszkan wspanialy = '0deUpgRxeiONMtk055LcoK'
    #top_of_the_top_u = '0k5DCITU0LEZZkgul7Ey5M'
    #top_adam = '6MBd4UoRtoeoe8shYu2ioj'
    #top_pio = '4Q5z9tpuyoIlXvNeSkV3A3'


    #specific_workflows.remove_dupes_within_playlists(spotify, '0deUpgRxeiONMtk055LcoK', renew_data=False)
    #specific_workflows.sync_mieszkan(spotify, renew_data=True, remove_or_log_flag=True)
    #specific_workflows.print_playlist(spotify, '4x1n7HZJsLfx548o9Ccc3L')
    #specific_workflows.log_artists_song_no(spotify, '0deUpgRxeiONMtk055LcoK')
    specific_workflows.random_mieszkan_stats(spotify)
    #stats.make_all_stats(spotify, '0deUpgRxeiONMtk055LcoK0')

1