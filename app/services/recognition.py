from __future__ import annotations

from django.core.files.uploadedfile import InMemoryUploadedFile

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import vosk
import wave
from json import loads
import random
import os
import librosa
from io import BytesIO
from scipy.io import wavfile

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import torchaudio
from speechbrain.pretrained import EncoderClassifier
print('Не беспокойтесь, предупреждения выше ни на что не влияют.')

from app.services import commands # необходимо для запуска функций из модуля через exec
from app.services.words import RU_DATA_SET, EN_DATA_SET, NOT_UNDERSTAND_ANSWERS
from app.services.voices import get_audio_data_silero, get_audio_data_gtts
from app.services.gpt import get_gpt_answer
from app.services.utils import download_and_unpack_zip_to_folder


# https://huggingface.co/speechbrain/lang-id-voxlingua107-ecapa
# https://bark.phon.ioc.ee/voxlingua107/
classifier = EncoderClassifier.from_hparams(
    source='app/static/app/models/lang-id-voxlingua107-ecapa',
    savedir='app/static/app/models/lang-id-voxlingua107-ecapa'
)
classifier.hparams.label_encoder.ignore_len()


vosk.SetLogLevel(-1) # отключить лог воска

if os.environ.get('PERMANENT_USE_SMALL_MODEL'):
    vosk_models_path = 'app/static/app/models/vosk_small/'
else:
    vosk_models_path = 'app/static/app/models/vosk_large/'

if not os.path.exists(vosk_models_path + 'ru/am') or not os.path.exists(vosk_models_path + 'en/am'):
    vosk_models_path = 'app/static/app/models/vosk_small/'

if not os.path.exists(vosk_models_path + 'ru/am'):
    download_and_unpack_zip_to_folder(
        'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip',
        vosk_models_path,
        'ru'
    )

if not os.path.exists(vosk_models_path + 'en/am'):
    download_and_unpack_zip_to_folder(
        'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        vosk_models_path,
        'en'
    )

# https://alphacephei.com/vosk/models
model_ru = vosk.Model(vosk_models_path + 'ru')
model_en = vosk.Model(vosk_models_path + 'en')

vosk_models = {'ru': model_ru, 'en': model_en}

# Обучаем матрицу ИИ на DATA_SET модели для распознавания команд ассистентом
ru_vectorizer = CountVectorizer()
ru_vectors = ru_vectorizer.fit_transform(list(RU_DATA_SET.keys()))

ru_regression = LogisticRegression()
ru_regression.fit(ru_vectors, list(RU_DATA_SET.values()))

en_vectorizer = CountVectorizer()
en_vectors = en_vectorizer.fit_transform(list(EN_DATA_SET.keys()))

en_regression = LogisticRegression()
en_regression.fit(en_vectors, list(EN_DATA_SET.values()))

vectorizers = {'ru': ru_vectorizer, 'en': en_vectorizer}
regressions = {'ru': ru_regression, 'en': en_regression}



def predict_probability_belong_embedded_cmd(request_text: str, lang_code: str) -> str | None:
    """Анализ распознанной речи для определения
    принадлежности запроса к встроенным командам"""

    # получаем вектор основанный на тексте из аудио
    # сравниваем с данными из дата сета, получая наиболее подходящий ответ
    user_command_vector = vectorizers[lang_code].transform([request_text])

    # Предсказание вероятностей принадлежности к каждой команде
    predicted_probabilities = regressions[lang_code].predict_proba(user_command_vector)

    # Поиск наибольшей вероятности
    max_probability = max(predicted_probabilities[0])
    print('max_probability:', max_probability)

    data_set_val = regressions[lang_code].classes_[predicted_probabilities[0].argmax()]

    # Коэффициент порога совпадения (необходимо подстраивать под наполнение дата сета)
    threshold = 0.53

    # возвращает значение дата сета, если значение вероятности
    # больше значения порогового коэффициента, иначе возвращает None
    return data_set_val if max_probability >= threshold else None



def branching_logic(request_text: str, lang_code: str) -> bytes:
    """Ветвление логики на запрос к GPT либо выполнение встроенных команд"""

    # print('request_text:', request_text)
    if not request_text:
        return get_audio_data_gtts(random.choice(NOT_UNDERSTAND_ANSWERS[lang_code]))

    data_set_val: str | None = predict_probability_belong_embedded_cmd(request_text, lang_code)

    if data_set_val is None:
        gpt_answer, gpt_code = get_gpt_answer(request_text)

        return get_audio_data_gtts(
            gpt_answer if gpt_answer else random.choice(NOT_UNDERSTAND_ANSWERS[lang_code]),
            lang_code
        )

    # получение имени функции и сообщения из значения дата сета
    func_name, answer_phrase = data_set_val.split(maxsplit=1)

    # запуск функции из файла commands
    exec(f'commands.{func_name}("{request_text}", "{lang_code}", "{answer_phrase}")')
    return get_audio_data_silero(answer_phrase, lang_code)



def recognize_lang_from_audio_file(audio_file_obj: InMemoryUploadedFile) -> str:
    """Распознование речи для получения кода языка"""

    # необходимо понизить частоту дискретизации для повышения шанса распознования
    numpy_arr, sample_rate = librosa.load(audio_file_obj, sr=16000) # Downsample to 16kHz
    bytes_io = BytesIO(bytes())
    wavfile.write(bytes_io, 16000, numpy_arr)

    signal, sample_rate = torchaudio.load(bytes_io)
    print('sample_rate:', sample_rate)

    embeddings = classifier.encode_batch(signal)

    out_prob, score, index, text_lab = classifier.classify_batch(signal)
    print('text_lab:', text_lab)

    lang_code, lang_name = text_lab[0].split(': ')
    print(f'Скорее всего это язык: {lang_name} с шансом: {score.exp()[0] :.0%}')

    allowed_lang_codes = ['ru', 'en']

    if lang_code not in allowed_lang_codes:
        lang_code = 'ru'
        print(f'Язык не попал в список разрешённых: {allowed_lang_codes}, изменяю язык на: {lang_code}')

    return lang_code



def recognize_text_from_audio_file(audio_file_obj: InMemoryUploadedFile) -> bytes:
    """Распознование речи для преобразования в текст"""

    # https://github.com/alphacep/vosk-api/blob/master/python/example/test_alternatives.py
    wave_audio_file_obj = wave.open(audio_file_obj, 'rb')

    if ( wave_audio_file_obj.getnchannels() != 1 
    or wave_audio_file_obj.getsampwidth() != 2 
    or wave_audio_file_obj.getcomptype() != 'NONE' ):
        print('Audio file must be WAV format mono PCM.')
        return get_audio_data_silero('Аудио файл должен иметь вейв формат моно писиэм')

    audio_file_obj.seek(0)
    lang_code = recognize_lang_from_audio_file(audio_file_obj)
    audio_file_obj.seek(0)

    recognizer = vosk.KaldiRecognizer(
        vosk_models[lang_code],
        wave_audio_file_obj.getframerate()
    )
    recognizer.SetMaxAlternatives(1) # макс количество результатов
    recognizer.SetWords(True)

    while True:
        data = wave_audio_file_obj.readframes(4000)
        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = loads(recognizer.Result())
            # print('result:', result)

            return branching_logic(result['alternatives'][0]['text'], lang_code)
