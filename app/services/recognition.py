from __future__ import annotations

from django.core.files.uploadedfile import InMemoryUploadedFile

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import vosk
import wave
from json import loads
import random

from app.services import commands # необходимо для запуска функций из модуля через exec
from app.services.words import DATA_SET
from app.services.voices import get_audio_data_silero, get_audio_data_gtts
from app.services.gpt import get_gpt_answer


vosk.SetLogLevel(-1) # отключить лог воска
model_ru = vosk.Model('app/static/app/models/vosk_small/ru')

# Обучаем матрицу ИИ на DATA_SET модели для распознавания команд ассистентом
vectorizer = CountVectorizer()
vectors = vectorizer.fit_transform(list(DATA_SET.keys()))

clf = LogisticRegression()
clf.fit(vectors, list(DATA_SET.values()))

# Коэффициент порога совпадения
threshold = 0.2

not_understand_answers = (
    'Я не поняла',
    'Не смогла разобрать повтори ещё раз пожалуйста',
    'Не расслышала',
    'Повтори ещё один раз пожалуйста',
    'Повтори',
    'Скажи ещё раз'
)


def is_builtin_cmd(text: str) -> str | None:
    """Анализ распознанной речи"""

    # получаем вектор основанный на тексте из аудио
    # сравниваем с данными из дата сета, получая наиболее подходящий ответ
    user_command_vector = vectorizer.transform([text])

    # Предсказание вероятностей принадлежности к каждой команде
    predicted_probabilities = clf.predict_proba(user_command_vector)

    # Поиск наибольшей вероятности
    max_probability = max(predicted_probabilities[0])

    data_set_val = clf.classes_[predicted_probabilities[0].argmax()]

    # возвращает значение дата сета, если значение вероятности
    # больше значения порогового коэффициента, иначе возвращает None
    return data_set_val if max_probability >= threshold else None


def recognize(text: str) -> bytes:
    """Ветвление логики на запрос к GPT и выполнение встроенных команд"""

    if not text:
        return get_audio_data_gtts(random.choice(not_understand_answers))

    data_set_val: str | None = is_builtin_cmd(text)

    if data_set_val is None:
        answer, code = get_gpt_answer(text)
        return get_audio_data_gtts(answer if answer else random.choice(not_understand_answers))

    # получение имени функции и сообщения из значения дата сета
    func_name, answer = data_set_val.split(maxsplit=1)

    # запуск функции из файла commands
    exec(f'commands.{func_name}()')
    return get_audio_data_silero(answer)


def recognize_wheel(audio_data: InMemoryUploadedFile) -> bytes:
    """Распознование речи"""

    # https://github.com/alphacep/vosk-api/blob/master/python/example/test_alternatives.py
    file = wave.open(audio_data, 'rb')

    if file.getnchannels() != 1 or file.getsampwidth() != 2 or file.getcomptype() != 'NONE':
        print('Audio file must be WAV format mono PCM.')
        return get_audio_data_silero('Аудио файл должен иметь вейв формат моно писиэм')

    recognizer = vosk.KaldiRecognizer(model_ru, file.getframerate())
    recognizer.SetMaxAlternatives(1) # макс количество результатов
    recognizer.SetWords(True)

    while True:

        data = file.readframes(4000)
        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = loads(recognizer.Result())
            return recognize(result['alternatives'][0]['text'])
