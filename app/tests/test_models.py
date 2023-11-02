from io import BytesIO

from django.test import TestCase

from torch.cuda import is_available
from scipy.io import wavfile
import librosa
import torchaudio
from speechbrain.pretrained import EncoderClassifier


# python manage.py test app.tests.test_models.TestCorrectnessClassifierModels
class TestCorrectnessClassifierModels(TestCase):

    @classmethod
    def setUpTestData(cls):

        voxlingua107_classifier = EncoderClassifier.from_hparams(
            source='app/static/app/models/lang-id-voxlingua107-ecapa',
            savedir='app/static/app/models/lang-id-voxlingua107-ecapa',
            # https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda_12.2.2_537.13_windows.exe
            run_opts={"device": "cuda"} if is_available() else None
        )
        voxlingua107_classifier.hparams.label_encoder.ignore_len()

        commonlanguage_classifier = EncoderClassifier.from_hparams(
            source='app/static/app/models/lang-id-commonlanguage_ecapa',
            savedir='app/static/app/models/lang-id-commonlanguage_ecapa',
            run_opts={"device": "cuda"} if is_available() else None
        )
        commonlanguage_classifier.hparams.label_encoder.ignore_len()

        cls.classifiers = {'voxlingua107': voxlingua107_classifier, 'commonlanguage': commonlanguage_classifier}

        cls.file_names = (
            'ru_nums_test.wav',
            'ru_text_test.wav',
            'ru_five_years_test.wav',

            'en_nums_test.wav',
            'en_text_test.wav',
            'en_five_years_test.wav',
        )

    def test_classifier(self):

        for model_name, classifier in self.classifiers.items():
            for file_name in self.file_names:
                correct_lang_code = file_name[:2]

                # необходимо понизить частоту дискретизации для повышения шанса распознования
                numpy_arr, sample_rate = librosa.load(
                    'app/static/app/audios/' + file_name, sr=16000) # Downsample to 16kHz
                bytes_io = BytesIO(bytes())
                wavfile.write(bytes_io, 16000, numpy_arr)

                signal, sample_rate = torchaudio.load(bytes_io)

                out_prob, score, index, text_lab = classifier.classify_batch(signal)

                lang_name = text_lab[0].split(': ')[-1]
                lang_code = lang_name[:2].lower()
                exp = f'{score.exp()[0] :.0%}'

                print(f'| Модель: {model_name :14} | Файл: {file_name :22} | Скорее всего это язык: {lang_name :9} | с шансом: {exp :4} |')

                # self.assertEqual(correct_lang_code, lang_code)
