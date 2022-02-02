import os
import pickle
import requests
from init_photo_service import Create_Service


API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'client_secret_photo_sync_service.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']
DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, SCOPES)

token = pickle.load(open('token_photoslibrary_v1.pickle', 'rb'))
source_folder = r'.\CacheFolder'
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
send_tokens = []


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



image_1 = os.path.join(source_folder, 'NewScreenshot_20220104-194424.png')
response = upload_image(image_1, os.path.basename(image_1), token)
send_tokens.append(response.content.decode('utf-8'))

image_2 = os.path.join(source_folder, 'NewScreenshot_20220104-194437.png')
response = upload_image(image_2, os.path.basename(image_2), token)
send_tokens.append(response.content.decode('utf-8'))

image_3 = os.path.join(source_folder, 'NewScreenshot_20220104-194444.png')
response = upload_image(image_3, os.path.basename(image_3), token)
send_tokens.append(response.content.decode('utf-8'))

new_media_items = [{'simpleMediaItem': {'uploadToken': each_token}} for each_token in send_tokens]

request_body = {
    'newMediaItems': new_media_items
}

upload_response = service.mediaItems().batchCreate(body=request_body).execute()