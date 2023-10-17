import urllib.request
from io import BytesIO
from zipfile import ZipFile


def download_and_unpack_zip_to_folder(
    url: str, unpack_to: str='', new_name_unpacked_folder: str=''):

    folder_name_with_ext = url.rsplit('/', maxsplit=1)[-1]
    folder_name_without_ext = folder_name_with_ext.rsplit('.', maxsplit=1)[0]

    print(f'Начинаю загрузку архива: {folder_name_with_ext}')

    response = urllib.request.urlopen(url)

    buffer = BytesIO(response.read())
    with ZipFile(buffer) as file:

        if new_name_unpacked_folder:
            NameToInfo = {}
            for file_name, file_obj in file.NameToInfo.items():
                file_name = file_name.replace(
                    folder_name_without_ext,
                    new_name_unpacked_folder
                )
                file_obj.filename = file_obj.filename.replace(
                    folder_name_without_ext,
                    new_name_unpacked_folder
                )
                NameToInfo[file_name] = file_obj
            file.NameToInfo = NameToInfo

            filelist = []
            for file_obj in file.filelist:
                file_obj.filename = file_obj.filename.replace(
                    folder_name_without_ext,
                    new_name_unpacked_folder
                )
                filelist.append(file_obj)
            file.filelist = filelist

        file.extractall(unpack_to)

    print(f'Успешно завершена загрузка и распаковка архива: {folder_name_with_ext} \
в директорию: {unpack_to + new_name_unpacked_folder}')
