from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.handlers.asgi import ASGIRequest

from app.services.recognition import recognize_text_from_audio_file


class AiVoiceHelperView(TemplateView):

    template_name = 'app/ai_voice_helper.html'

    def post(self, request: ASGIRequest, *args, **kwargs):

        audio_file_obj = request.FILES.get('audio_data')

        # сохранить аудио локально (для тестов)
        # with open(f'app/static/app/audios/{audio_file_obj.name}', 'wb+') as file:
        #     for chunk in audio_file_obj.chunks():
        #         file.write(chunk)

        # вернуть аудио на фронт как оно есть (для тестов)
        # with open('app/static/app/audios/en_nums_test.wav', 'rb') as file:
        #     audio_file_obj = file.read()

        # вернуть аудио на фронт переозвученное другим голосом (для тестов)
        # audio_file_obj = recognize_text_from_audio_file('app/static/app/audios/ru_nums_test.wav')

        audio_file_obj = recognize_text_from_audio_file(audio_file_obj)

        # audio_file_obj = b'' # заглушка
        return HttpResponse(audio_file_obj, content_type='audio/wav; codecs=pcm')
