from __future__ import annotations

import wave
import json
import random
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from vosk import KaldiRecognizer
from scipy.io import wavfile
import torchaudio
import librosa

from app.services import commands # необходимо для запуска функций из модуля через exec
from app.services.words import NOT_UNDERSTAND_ANSWERS
from app.services.voices import get_audio_data_silero, get_audio_data_gtts
from app.services.gpt import get_gpt_answer
from app.services.models_load import (
    vectorizers, regressions, classifiers, vosk_models
)



def predict_probability_belong_embedded_cmd(request_text: str, lang_code: str) -> str | None:
    """Анализ распознанной речи для определения
    принадлежности запроса к встроенным командам"""

    # получаем вектор основанный на тексте из аудио
    # сравниваем с данными из дата сета, получая наиболее подходящий ответ
    user_command_vector = vectorizers[lang_code].transform([request_text])

    # Предсказание вероятностей принадлежности к каждой команде
    predicted_probabilities = regressions[lang_code].predict_proba(user_command_vector)

    # Коэффициент порога совпадения (необходимо подстраивать под наполнение дата сета)
    threshold = 0.53

    # Поиск наибольшей вероятности
    max_probability = max(predicted_probabilities[0])
    print('\nпорог:', threshold, 'вероятность:', max_probability)

    data_set_val = regressions[lang_code].classes_[predicted_probabilities[0].argmax()]

    # возвращает значение дата сета, если значение вероятности
    # больше значения порогового коэффициента, иначе возвращает None
    return data_set_val if max_probability >= threshold else None



def branching_logic(request_text: str, lang_code: str) -> tuple[bytes, str]:
    """Ветвление логики на запрос к GPT либо выполнение встроенных команд"""

    print(f'\n{"—"*25}Текст запроса{"—"*25}\n{request_text}\n{"—"*25}Текст запроса{"—"*25}')
    if not request_text:
        return get_audio_data_gtts(random.choice(NOT_UNDERSTAND_ANSWERS[lang_code]))

    data_set_val: str | None = predict_probability_belong_embedded_cmd(request_text, lang_code)

    if data_set_val is None:
        gpt_answer, gpt_code = get_gpt_answer(request_text)

        return get_audio_data_gtts(
            gpt_answer if gpt_answer else random.choice(NOT_UNDERSTAND_ANSWERS[lang_code]),
            lang_code
        ), gpt_code

    # получение имени функции и сообщения из значения дата сета
    func_name, answer_phrase = data_set_val.split(maxsplit=1)

    # запуск функции из файла commands
    exec(f'commands.{func_name}("{request_text}", "{lang_code}", "{answer_phrase}")')
    return get_audio_data_silero(answer_phrase, lang_code), ''



def recognize_lang_from_audio_file(audio_file_obj: InMemoryUploadedFile) -> str:
    """Распознование речи для получения кода языка"""

    # необходимо понизить частоту дискретизации для повышения шанса распознования
    numpy_arr, sample_rate = librosa.load(audio_file_obj, sr=16000) # Downsample to 16kHz
    bytes_io = BytesIO(bytes())
    wavfile.write(bytes_io, 16000, numpy_arr)

    signal, sample_rate = torchaudio.load(bytes_io)
    # print('sample_rate:', sample_rate)

    for model_name, classifier in classifiers.items():

        out_prob, score, index, text_lab = classifier.classify_batch(signal)
        # print('text_lab:', text_lab)

        lang_name = text_lab[0].split(': ')[-1]
        lang_code = lang_name[:2].lower()
        exp = f'{score.exp()[0] :.0%}'

        print(f'Модель: {model_name} Скорее всего это язык: {lang_name} с шансом: {exp}')

        allowed_lang_codes = ['ru', 'en']

        if lang_code not in allowed_lang_codes:
            lang_code = 'ru'
            print(f'Язык: {lang_name} не попал в список разрешённых: {allowed_lang_codes}, изменяю язык на: {lang_code}')
        else:
            break

    return lang_code



def recognize_text_from_audio_file(audio_file_obj: InMemoryUploadedFile) -> tuple[bytes, str]:
    """Распознование речи для преобразования в текст"""

    # https://github.com/alphacep/vosk-api/blob/master/python/example/test_alternatives.py
    wave_audio_file_obj: wave.Wave_read = wave.open(audio_file_obj, 'rb')

    if ( wave_audio_file_obj.getnchannels() != 1 
    or wave_audio_file_obj.getsampwidth() != 2 
    or wave_audio_file_obj.getcomptype() != 'NONE' ):
        print('Audio file must be WAV format mono PCM.')
        return get_audio_data_silero('Аудио файл должен иметь вейв формат моно писиэм')

    if isinstance(audio_file_obj, InMemoryUploadedFile):
        audio_file_obj.seek(0)

    lang_code = recognize_lang_from_audio_file(audio_file_obj)

    if isinstance(audio_file_obj, InMemoryUploadedFile):
        audio_file_obj.seek(0)

    recognizer = KaldiRecognizer(
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
            result = json.loads(recognizer.Result())
            # print('result:', result)

            return branching_logic(result['alternatives'][0]['text'], lang_code)
