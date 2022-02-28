import os
import requests
import pandas as pd
from init_photo_service import Create_Service

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
endpoint = 'mediaget_endpoint'

dl_service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, endpoint, SCOPES)


def main(source_album):
    dir = r'.\CacheFolder'
    for f in os.listdir(dir):
        print('Deleting Cache', f)
        os.remove(os.path.join(dir, f))
    album_id = get_album_id(source_album)
    if album_id == ():
        exit()
    else:
        dl_album(album_id)
    return


def get_album_id(source_album):
    try:
        response_albums = dl_service.albums().list(
            pageSize=50,
            excludeNonAppCreatedData=False
        ).execute()
        albums = response_albums.get('albums')
        next_page_token = response_albums.get('nextPageToken')
        while next_page_token:
            response_albums = dl_service.albums().list(
                pageSize=50,
                excludeNonAppCreatedData=False,
                pageToken=next_page_token
            ).execute()
            if response_albums.get('albums') is not None:
                albums.extend(response_albums.get('albums'))
            next_page_token = response_albums.get('nextPageToken')
        df_albums = pd.DataFrame(albums,
                                 columns=['id', 'title', 'productURL', 'mediaItemsCount', 'coverPhotoBaseURL',
                                          'coverMediaID'])
        print(df_albums['title'])
        ret_album_id = df_albums[df_albums['title'] == source_album]['id'].to_string(index=False).strip()
        return ret_album_id
    except Exception as e:
        print('Unable to find Album in get_album_id')
        print(e)
    return ()


def download_file(url: str, local_folder: str, source_file: str):
    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading file {0}'.format(source_file))
        with open(os.path.join(local_folder, source_file), 'wb') as f:
            f.write(response.content)
            f.close()


def dl_album(dl_album_id):
    try:
        destination_folder = r'.\CacheFolder'
        media_files = None
        next_page_token = 'IsNull'
        count = 0
        while next_page_token is not None:
            next_page_token = '' if next_page_token == 'IsNull' else next_page_token
            media_files_results = dl_service.mediaItems().search(
                body={'albumId': dl_album_id, "pageSize": 100, 'pageToken': next_page_token}).execute()
            if next_page_token != '':
                media_files.append(media_files_results.get('mediaItems'))
                next_page_token = media_files_results.get('nextPageToken')
                count= count+1
                print(count, ' - ', next_page_token)
            else:
                media_files = media_files_results.get('mediaItems')
                next_page_token = media_files_results.get('nextPageToken')
        for media_file in media_files:
            file_name = media_file['filename']
            download_url = media_file['baseUrl'] + '=d'
            download_file(download_url, destination_folder, file_name)
    except Exception as e:
        print('Unable to find %s Album.')
    return None


if __name__ == "__main__":
    main()