import os
from init_photo_service import Create_Service
import pandas as pd  # pip install pandas
import requests  # pip install requests

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_colwidth', 150)
pd.set_option('display.width', 150)
pd.set_option('expand_frame_repr', True)

API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'client_secret_photo_sync_service.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']
DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, SCOPES)


def get_album_id(source_album):
    try:
        next_page_token = None
        albums = service.albums().list(pageSize=50).execute()
        next_page_token = albums.get('nextPageToken')
        while next_page_token:
            response = service.albums().list(
                pageSize=50,
                pageToken=next_page_token
            ).execute()
        albums_list = albums.get('albums')
        df_albums = pd.DataFrame(albums_list)
        ret_album_id = df_albums[df_albums['title'] == source_album]['id'].to_string(index=False).strip()
        return ret_album_id
    except Exception as e:
        print('Unable to find Album in get_album_id')
    return ()


def download_file(url: str, local_folder: str, source_file: str):
    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading file {0}'.format(source_file))
        with open(os.path.join(local_folder, source_file), 'wb') as f:
            f.write(response.content)
            f.close()

def dl_album(album_id):
    try:
        media_files = service.mediaItems().search(body={'albumId': album_id}).execute()['mediaItems']
        destination_folder = r'.\CacheFolder'
        for media_file in media_files:
            file_name = media_file['filename']
            download_url = media_file['baseUrl'] + '=d'
            download_file(download_url, destination_folder, file_name)
    except Exception as e:
        print('Unable to find Album.')
        print(e)
    return None


fixed_source = "Recipes"
album_id = get_album_id(fixed_source)
if album_id == ():
    exit()
else:
    dl_album(album_id)




