import gtts
from io import BytesIO
import os
import torch
from IPython.display import Audio


device = torch.device('cpu')
torch.set_num_threads(4)

model_ru = torch.package.PackageImporter(
    'app/static/app/models/silero_models/ru/v3_1_ru.pt'
).load_pickle("tts_models", "model")

model_en = torch.package.PackageImporter(
    'app/static/app/models/silero_models/en/v3_en.pt'
).load_pickle("tts_models", "model")

model_ru.to(device)
model_en.to(device)

silero_models = {'ru': model_ru, 'en': model_en}

speakers = {
    'ru': 'kseniya', # aidar, baya, kseniya, xenia, eugene
    'en': 'en_0' # от 0 до 117 номера разных спикеров
}

sample_rate = 48000
filename = 'ai_voice_helper.wav'



def get_audio_data_silero(text: str, lang_code: str='ru') -> bytes:
    """Озвучка текста моделью silero\n
    Может работать только с одним языком одиновременно (не поддерживает смешивание)"""

    numpy_arr = silero_models[lang_code].apply_tts(
        text=text,
        speaker=speakers[lang_code],
        sample_rate=sample_rate
    )

    file = Audio(numpy_arr, rate=sample_rate)
    file.filename = filename

    return file.data



def get_audio_data_gtts(text: str, lang_code: str='ru') -> bytes:
    """Озвучка текста моделью gtts\n
    Поддерживает смесь языков в тексте"""

    with BytesIO() as file:

        try:
            gtts.gTTS(text, lang=lang_code).write_to_fp(file)
        except gtts.tts.gTTSError as exc:
            print('def get_audio_data_gtts:', exc)
            return b''

        # После записи в файл указатель оказался в самом конце,
        # поэтому надо переместить указатель в самое начало файла методом seek
        file.seek(0)

        # запоминаем изначальную позицию указателя,
        # затем пробегаемся указателем от начала до конца файла для получения размера,
        # в конце возвращаем изначальную позицию указателя
        init_pos_pointer = file.tell()
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(init_pos_pointer, os.SEEK_SET)

        return file.read1(size)
