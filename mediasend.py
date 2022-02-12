import os
import pickle
import requests
import pandas as pd
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
# def find_media_id(album):
#     response = service.mediaItems().search().execute()
#     found_medias = response.get('mediaItems')
#     nextPageToken = response.get('nextPageToken')
#
#     while nextPageToken:
#         response = service.mediaItems().search(
#             pageSize=100,
#             pageToken=nextPageToken
#         ).execute()
#
#         found_medias.extend(response.get('mediaItems'))
#         nextPageToken = response.get('nextPageToken')
#
#     print(found_medias)
#     df_media_items = pd.DataFrame(found_medias)
#     print(df_media_items)
#     media_id = df_media_items.loc[df_media_items['filename'] == album, 'id'].values[0]
# #    print(df_media_items['id'].where(df_media_items['filename'] is album))
#
#     # for album in df_media_items['filename']:
#     #     album_id = df_media_items['id']
#     #     print(album_id)
#     # media_id = df_media_items['id'][108]
#     # response = service.mediaItems().get(mediaItemId=media_id).execute()
#     return media_id


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
#    new_media_items = [{'simpleMediaItem': {'uploadToken': each_token}} for each_token in send_tokens]
    header_album_id = (commit_album_id)
    for each_token in [send_tokens]:
        if each_token == None:
            print('No Token Found')
            return
        else:
            each_token = "".join(each_token)
            continue

    request_body = (
       f'{{'
       f'     "albumId": {header_album_id},'
       f'     "newMediaItems": ['
       f'         {{'
       f'             "description": "item-description",'
       f'             "simpleMediaItem": {{'
       f'                 "fileName": "filename",'
       f'                 "uploadToken": {each_token}'
       f'             }}'
       f'         }}'
#      f'         , ...'
       f'     ]'
#      f'     "albumPosition": {'
#      f'         "position": "after-media-item",'
#      f'         "relativeMediaItemId": "media-item-id"'
#      f'     }'
        f'}}'
    )


    upload_response = service.mediaItems().batchCreate(body=request_body).execute()
    return


# def list_media_id():
#     response = service.mediaItems().list(pageSize=100).execute()
#
#     lst_medias = response.get('mediaItems')
#     nextPageToken = response.get('nextPageToken')
#
#     while nextPageToken:
#         response = service.mediaItems().list(
#             pageSize=100,
#             pageToken=nextPageToken
#         ).execute()
#
#         lst_medias.extend(response.get('mediaItems'))
#         nextPageToken = response.get('nextPageToken')
#
#     df_media_items = pd.DataFrame(lst_medias)
#     print(df_media_items)
#     # media_id = df_media_items['id'][108]
#     # response = service.mediaItems().get(mediaItemId=media_id).execute()
#     return

# 'NewScreenshot_20220104-194437.png'
# 'NewScreenshot_20220104-194444.png'

# list_media_id()

source = r'.\CacheFolder'
filename = 'Screenshot_20220104-194424.png'
album_id = None
destination = "Recipes"
album_id = get_album_id(destination)
if album_id:
    album_id = album_id
else:
    create_album(destination)
# album_id = get_album_id(destination)
print(album_id)
token_response = queue_imagexfer(source, filename)
send_tokens.append(token_response.content.decode('utf-8'))
commit_transfer(album_id)
# testresult = find_media_id('DSC00256.JPG')
# print(testresult)