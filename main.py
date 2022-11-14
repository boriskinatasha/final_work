from token_my import token_vk
import requests
import urllib.request
from pprint import pprint
from datetime import datetime
from tqdm import tqdm
import os
import json


class UploaderPhotos:
    VK_GET_PHOTO: str = 'https://api.vk.com/method/photos.get'
    URL_UPLOAD_YA_DISK: str = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    def __init__(self, yd_token, id_user, count_photos=5):
        if count_photos == '':
            count_photos = 5
        self.headers_ya_disk = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {yd_token}'
        }

        self.params_vk = {
                'owner_id': id_user,
                'access_token': token_vk,
                'v': '5.131',
                'album_id': 'profile',
                'photo_sizes': 1,
                'extended': 1,
                'type': 'z',
                'count': count_photos
            }

    def get_user_profile_photos(self):
        try:
            res = requests.get(self.VK_GET_PHOTO, params=self.params_vk).json()
        except Exception as err:
            print(f'Произошла ошибка при взаимодействии с APi VK: {err}')
        else:
            items = res['response']['items']
        return items

    @staticmethod
    def create_photos_name(count_likes, date, dict_list, file_url):
        filename, file_extension = os.path.splitext(file_url)
        extension = file_extension.partition('?')[0]
        if count_likes in dict_list:
            date_convert = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')
            key_name = str(count_likes) + date_convert + extension
        else:
            key_name = str(count_likes) + extension
        return key_name

    def upload_user_profile_photos(self):
        items = self.get_user_profile_photos()
        dict_for_disk = dict()
        final_list = list()
        for item_vk in tqdm(items):
            file_url = item_vk['sizes'][-1]['url']
            key_name = self.create_photos_name(item_vk['likes']['count'], item_vk['date'], dict_for_disk, file_url)
            dict_for_disk[key_name] = item_vk['sizes'][-1]['url']

            params_ya_disk = {
                'path': 'vk_profile_photos/' + key_name,
                'overwrite': True
            }
            resp = requests.get(self.URL_UPLOAD_YA_DISK, headers=self.headers_ya_disk, params=params_ya_disk).json()
            upload_url = resp.get('href')
            file = urllib.request.urlopen(file_url).read()
            try:
                response = requests.put(upload_url, data=file)
            except Exception as err:
                print(f'Произошла ошибка при взаимодействии с APi Яндекс.Диск: {err}')
            else:
                if 200 <= response.status_code <= 299:
                    my_dict = dict()
                    my_dict['file_name'] = key_name
                    my_dict['size'] = item_vk['sizes'][-1]['type']
                    final_list.append(my_dict)
                with open('results.json', 'w') as j_file:
                    json.dump(final_list, j_file)
                return 'Информация о загруженных на диск фотографиях доступна в файле results.json'

token_ya_disk = ''

user_id = input('Введите идентификатор пользователя в VK: ')
c_photos = input('Укажите количество фотографий, которые необходимо загрузить с профиля или оставьте поле пустым (по умолчанию будет загружено 5 файлов): ')
vk_client = UploaderPhotos(token_ya_disk, user_id, c_photos)
pprint(vk_client.upload_user_profile_photos())
