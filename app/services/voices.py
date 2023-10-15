from gtts import gTTS
from io import BytesIO
import torch
from IPython.display import Audio


DEFAULT_CHUNK_SIZE = 64 * 2**10

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

speaker_ru = 'kseniya' # aidar, baya, kseniya, xenia, eugene
speaker_en = 'en_6' # от 0 до 117 номера разных спикеров

sample_rate = 44100
filename = 'filename'


def get_audio_data_silero(text: str, language: str='ru') -> bytes:
    """Озвучка текста моделью silero"""

    if language == 'ru':
        audio = model_ru.apply_tts(text=text, speaker=speaker_ru, sample_rate=sample_rate)
    elif language == 'en':
        audio = model_en.apply_tts(text=text, speaker=speaker_en, sample_rate=sample_rate)

    file = Audio(audio, filename, rate=sample_rate)

    return file.data


def get_audio_data_gtts(text: str, language: str='ru') -> bytes:
    """Озвучка текста моделью gtts"""

    with BytesIO() as file:

        gTTS(text, lang=language).write_to_fp(file)

        # Если с файлом взаимодействовали значит указатель не находится в начале файла,
        # поэтому надо переместить указатель в самое начало файла методом seek
        file.seek(0)

        return file.read1(DEFAULT_CHUNK_SIZE)
