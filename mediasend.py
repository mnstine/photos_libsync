import os
import pickle
import requests
import pandas as pd

import mediaget2
from init_photo_service import Create_Service


API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'client_secret_photo_sync_service.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']
DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, SCOPES)

token = pickle.load(open('token_photoslibrary_v1.pickle', 'rb'))
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
send_tokens = []


def create_album(album_name):
    request_body = {
        'album': {'title': album_name}
    }
    album_create_status = service.albums().create(body=request_body).execute()
    return album_create_status


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
#        textfile = open("albums_list.txt", "w")
#        textfile.write(albums_list)
#        textfile.close()
        df_albums = pd.DataFrame(albums_list)
        ret_album_id = df_albums[df_albums['title'] == source_album]['id'].to_string(index=False).strip()
        return ret_album_id
    except Exception as e:
        print('Unable to find Album in get_album_id')
    return ()


def upload_image(image_path, upload_file_name, ul_token):
    headers = {
        'Authorization': 'Bearer ' + ul_token.token,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Protocol': 'raw',
        'X-Goog-File-Name': upload_file_name
    }
    img = open(image_path, 'rb').read()
    ul_response = requests.post(upload_url, data=img, headers=headers)
    print('\nUpload token: {0}'.format(ul_response.content.decode('utf-8')))
    print(upload_file_name)
    return ul_response


def queue_imagexfer(img_folder, img_name):
    img_obj = os.path.join(img_folder, img_name)
    response = upload_image(img_obj, os.path.basename(img_obj), token)
    return response


def commit_transfer(commit_album_id):
    new_media_items = [{'simpleMediaItem': {'uploadToken': each_token}} for each_token in send_tokens]
    header_album_id = (commit_album_id)
    for each_token in [send_tokens]:
        if each_token == None:
            print('No Token Found')
            return
        else:
            each_token = "".join(each_token)
            continue
    request_body = {
        "albumId": header_album_id,
        "newMediaItems": [{'simpleMediaItem': {'uploadToken': each_token}}]
    }
    upload_response = service.mediaItems().batchCreate(body=request_body).execute()
    return


source = r'.\CacheFolder'
filename = '30426-20211017214041-Edit.jpg'
album_id = None
destination = "Recipes"
album_id = mediaget2.get_album_id(destination)
if album_id:
    album_id = album_id
else:
    create_album(destination)
    print('Created new Album')
print(album_id)
token_response = queue_imagexfer(source, filename)
send_tokens.append(token_response.content.decode('utf-8'))
commit_transfer(album_id)
# testresult = find_media_id('DSC00256.JPG')
# print(testresult)