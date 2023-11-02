import os

from torch import device, set_num_threads
from torch.package import PackageImporter
from torch.hub import download_url_to_file

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

from speechbrain.pretrained import EncoderClassifier
print('Не беспокойтесь, предупреждения выше ни на что не влияют.')

from vosk import Model, SetLogLevel
SetLogLevel(-1) # отключить лог воска

from app.services.words import RU_DATA_SET, EN_DATA_SET
from app.services.utils import download_and_unpack_zip_to_folder


# https://huggingface.co/speechbrain/lang-id-voxlingua107-ecapa
# https://bark.phon.ioc.ee/voxlingua107/
voxlingua107_classifier = EncoderClassifier.from_hparams(
    source='app/static/app/models/lang-id-voxlingua107-ecapa',
    savedir='app/static/app/models/lang-id-voxlingua107-ecapa'
)
voxlingua107_classifier.hparams.label_encoder.ignore_len()

# https://huggingface.co/speechbrain/lang-id-commonlanguage_ecapa
commonlanguage_classifier = EncoderClassifier.from_hparams(
    source='app/static/app/models/lang-id-commonlanguage_ecapa',
    savedir='app/static/app/models/lang-id-commonlanguage_ecapa'
)
commonlanguage_classifier.hparams.label_encoder.ignore_len()

classifiers = {'voxlingua107': voxlingua107_classifier, 'commonlanguage': commonlanguage_classifier}

if int(os.environ.get('PERMANENT_USE_SMALL_MODEL', '1')):
    print('Используется vosk_small')
    vosk_models_path = 'app/static/app/models/vosk_small/'
else:
    print('Используется vosk_large, ожидайте загрузку модели..')
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
model_ru = Model(vosk_models_path + 'ru')
model_en = Model(vosk_models_path + 'en')

vosk_models = {'ru': model_ru, 'en': model_en}

# Обучаем матрицу ИИ на DATA_SET модели для распознавания команд
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


silero_models_path = 'app/static/app/models/silero_models/'

if not os.path.exists(silero_models_path + 'ru/v3_1_ru.pt'):
    download_url_to_file(
        'https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
        silero_models_path + 'ru/v3_1_ru.pt'
    )

if not os.path.exists(silero_models_path + 'en/v3_en.pt'):
    download_url_to_file(
        'https://models.silero.ai/models/tts/en/v3_en.pt',
        silero_models_path + 'en/v3_en.pt'
    )

cpu_device = device('cpu')
set_num_threads(4)

model_ru = PackageImporter(
    'app/static/app/models/silero_models/ru/v3_1_ru.pt'
).load_pickle("tts_models", "model")

model_en = PackageImporter(
    'app/static/app/models/silero_models/en/v3_en.pt'
).load_pickle("tts_models", "model")

model_ru.to(cpu_device)
model_en.to(cpu_device)

silero_models = {'ru': model_ru, 'en': model_en}

speakers = {
    'ru': 'kseniya', # aidar, baya, kseniya, xenia, eugene
    'en': 'en_0' # от 0 до 117 номера разных спикеров
}
