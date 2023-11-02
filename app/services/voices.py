from os import SEEK_END, SEEK_SET
from io import BytesIO

from gtts import gTTS
from gtts.tts import gTTSError
from IPython.display import Audio

from app.services.models_load import silero_models, speakers


def get_audio_data_silero(text: str, lang_code: str='ru') -> bytes:
    """Озвучка текста моделью silero\n
    Может работать только с одним языком одиновременно (не поддерживает смешивание)"""

    numpy_arr = silero_models[lang_code].apply_tts(
        text=text,
        speaker=speakers[lang_code],
        sample_rate=48000
    )

    file = Audio(numpy_arr, rate=48000)
    file.filename = 'ai_voice_helper.wav'

    return file.data


def get_audio_data_gtts(text: str, lang_code: str='ru') -> bytes:
    """Озвучка текста моделью gtts\n
    Поддерживает смесь языков в тексте"""

    with BytesIO() as file:

        try:
            gTTS(text, lang=lang_code).write_to_fp(file)
        except gTTSError as exc:
            print('def get_audio_data_gtts:', exc)
            return get_audio_data_silero('Что то пошло не так')

        # После записи в файл указатель оказался в самом конце,
        # поэтому надо переместить указатель в самое начало файла методом seek
        file.seek(0)

        # запоминаем изначальную позицию указателя,
        # затем пробегаемся указателем от начала до конца файла для получения размера,
        # в конце возвращаем изначальную позицию указателя
        init_pos_pointer = file.tell()
        file.seek(0, SEEK_END)
        size = file.tell()
        file.seek(init_pos_pointer, SEEK_SET)

        return file.read1(size)
