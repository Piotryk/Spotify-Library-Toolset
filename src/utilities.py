
def make_artist_playlist(spotify, artist_id):
    """
    WORK IN PROGRESS. DO NOT USE
    Keep singles and EPs

    :param spotify:
    :param artist_id:
    :return:
    """
    '''
    response = spotify.artist_albums(artist_id, album_type=None, country=None, limit=20, offset=0)
    #artist_name = response['name']
    album_list = response['items']
    while response['next']:
        response = spotify.next(response)
        album_list.extend(response['items'])
    albums = [album for album in album_list if album['album_group'] != 'appears_on']
    '''
    pass