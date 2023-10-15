from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.handlers.asgi import ASGIRequest

from app.services.recognition import recognize_wheel


class AssistantView(TemplateView):

    template_name = 'app/assistant.html'

    def post(self, request: ASGIRequest, *args, **kwargs):

        audio_data = request.FILES.get('audio_data')

        # вернуть аудио на фронт как оно есть (для тестов)
        # with open('app/static/app/audios/en_nums_test.wav', 'rb') as file:
        #     audio_data = file.read()

        # вернуть аудио на фронт переозвученное другим голосом (для тестов)
        # audio_data = recognize_wheel('app/static/app/audios/ru_nums_test.wav')

        audio_data = recognize_wheel(audio_data)

        # audio_data = b'' # заглушка
        return HttpResponse(audio_data, content_type='audio/wav; codecs=pcm')
