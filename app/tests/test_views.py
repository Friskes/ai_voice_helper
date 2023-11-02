from time import sleep
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import soundfile
import sounddevice


# python manage.py test app.tests.test_views.TestAssistantView
class TestAssistantView(TestCase):

    @classmethod
    def setUpTestData(cls):

        file_names = (
            'ru_nums_test.wav',
            'ru_text_test.wav',
            'ru_five_years_test.wav',

            'en_nums_test.wav',
            'en_text_test.wav',
            'en_five_years_test.wav',
        )

        cls.ru_files_obj = []
        cls.en_files_obj = []

        for file_name in file_names:
            with open(f'app/static/app/audios/{file_name}', 'rb') as file:

                file_obj = SimpleUploadedFile(file_name, file.read(), content_type='audio/wav; codecs=pcm')

                if file_name.startswith('ru'):
                    cls.ru_files_obj.append(file_obj)

                elif file_name.startswith('en'):
                    cls.en_files_obj.append(file_obj)

    def test_post_request(self):

        for file_obj in self.ru_files_obj:
            self.play_response(file_obj)

        for file_obj in self.en_files_obj:
            self.play_response(file_obj)

    def play_response(self, file_obj):

        response = self.client.post(reverse('ai_voice_helper'), {'audio_data': file_obj})
        self.assertEqual(response.status_code, 200)

        with BytesIO() as file:
            file.write(response.content)
            file.seek(0)
            numpy_arr, sample_rate = soundfile.read(file)
            sounddevice.play(numpy_arr, sample_rate)

            # Принудительно останавливаю аудиозапись чтобы не затягивать тест
            sleep(3)
            sounddevice.stop()
