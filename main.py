import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_CLIENT_URL, SCOPE_MASTER

from src import current_playlists
from src import single_finder
from src import duplicates_finder
from src import merge
from src import stats
from src import stats_monthly_listeners
from src import utilities
from src import lyrics

"""
Only Merge and Uutilities edit spotify library.
Other features save results to .log files, so all found cases(single, duplicate etc.) needs to be removed manually.

TODO:
    Check_id currently can check only ids from my spotify. Find better way to check any playlist id
    Fill parameters in function comments
    Exceptions have hardcoded file names. Move filenames to variables in case of update
    Fix printing playlist name in download lyrics 
    Fix printing playlist name in sources check
    
    Utilities:
    Making playlist with every song added to sources in last 6 months?
    Making playlist with every song of specific artist
"""


if __name__ == '__main__':
    '''
    IDs of playlists I want to process
    '''
    # My playlists ids
    wszystko_id = '5ILM7FGO30AanFwmfuLXVB'
    allar_id = '6UTHiiydwvjK1NZ7mZ7u7O'
    #allpol_id = '5GJ9VxkT1qqB53inWdOXL8'   # Removed from spotify
    top_id = '0AwOdQZaWhm5uXrE507LHg'
    pl_klasyki_id = '7MWE8HgYpzcyLPrXYvKrF2'

    top_toczek_id = '4Q5z9tpuyoIlXvNeSkV3A3'
    rzeczy_toczek_id = '2sSlxwInCbM51QoiVgHWj9'
    mdm_id = '44TdhggxmyUm95R6ce1LIL'

    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt']
    merged = ['playlists/merged.txt']
    all_source_files = ['playlists/merged.txt', 'playlists/skip.txt'] + sources
    all_playlists_file = 'playlists/all_playlists.txt'
    #playlists = [top_id, wszystko_id, allar_id, pl_klasyki_id, top_toczek_id, rzeczy_toczek_id, mdm_id]
    playlists = [top_id, wszystko_id, allar_id, pl_klasyki_id]
    check = True

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                                        redirect_uri=SPOTIPY_CLIENT_URL,
                                                        scope=SCOPE_MASTER))

    lyrics.get_lyrics_from_sources(spotify, sources, check_existing_file=True, preserve_logs=False)

    '''
    Check if ids declared above are still valid. Commented out due to aggresive behaviour
    '''
    #utilities.check_ids(playlists)

    '''
    Get all user's playlists to all_playlists.txt
    '''
    current_playlists.get_playlists(spotify, all_playlists_file)

    '''
    Check if all spotify playlists are in sources
    And if all playlists in sources are still in spotify library
    
    Second check if all specific ids above still exist on Spotify
    NOTE: 
    '''
    if not current_playlists.sanity_check(all_source_files, all_playlists_file):
        sys.exit(-2)

    if not current_playlists.check_ids(playlists, all_playlists_file):
        sys.exit(-3)

    '''
    Find songs from single release or EP, but they shoud be removed or marked as allowed manually
    Found singles are listed in log file
    '''
    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt', 'playlists/skip.txt']
    single_finder.find_singles(spotify, sources)

    ''' 
    Finding songs that occur on two different playlists on sources. There should be no such songs
    Finding artists that populate more than one playlists. Exceptions are based on specific song
    '''
    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt']
    duplicates_finder.find_duplicaded_songs(spotify, sources)
    duplicates_finder.find_duplicated_artists(spotify, sources)

    '''
    Check if all songs on merged playlists are on sources
    '''
    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt']
    merged = ['playlists/merged.txt']
    merge.check_merged_simple(spotify, merged, sources)
    merge.check_merged(spotify, merged, sources)

    '''
    Add all songs form sources to target playlist.
    Omit songs that are already on target
    '''
    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt']
    merge.merge(spotify, ['playlists/sources_ar.txt'], allar_id, add_in_doubt=False)
    #merge.merge(spotify, ['playlists/sources_pl.txt'], allpol_id)
    merge.merge(spotify, sources, wszystko_id)
    merge.check_merged(spotify, merged, sources)

    '''
    Get lyrics from all songs and save them in one file (data/lyrics.txt)
    Unfortunately looking for PL / RUS / specyficzne is pointless.
    '''
    sources = ['playlists/sources_ar.txt', 'playlists/sources_niear.txt', 'playlists/sources_pl.txt']
    #lyrics.get_lyrics_from_playlist(spotify, wszystko_id, check_existing_file=True, preserve_logs=False)
    lyrics.get_lyrics_from_sources(spotify, sources, check_existing_file=True, preserve_logs=False)

    '''
    Make some stats for set of playlists
    '''
    playlists = [top_id, allar_id, wszystko_id, top_toczek_id, rzeczy_toczek_id]
    #playlists = [top_id]
    stats.make_all_stats(spotify, playlists)

    #utilities.get_artists_to_file(spotify, [top_id, allar_id, wszystko_id, top_toczek, rzeczy_toczek, pl_klasyki_id, mdm_id])     # in case I need to renew the monthly listeners data
    stats_monthly_listeners.make_stats(spotify, playlists)

    stats.artists_in_first_n_songs_compare(spotify, top_toczek_id, top_id, shuffle=False)
    stats.artists_in_first_n_songs_compare(spotify, rzeczy_toczek_id, allar_id, shuffle=True, fit=True)
