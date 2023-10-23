from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.handlers.asgi import ASGIRequest
from django.core.files.uploadedfile import InMemoryUploadedFile

from base64 import b64encode

from app.services.recognition import recognize_text_from_audio_file
from app.services.words import RU_DATA_SET, EN_DATA_SET



class AiVoiceHelperView(TemplateView):

    template_name = 'app/ai_voice_helper.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        language = self.request.META.get('HTTP_ACCEPT_LANGUAGE')
        lang_code = language[:2] if language else 'ru'

        if lang_code == 'ru':
            context.update({'embedded_commands': RU_DATA_SET.keys()})
        elif lang_code == 'en':
            context.update({'embedded_commands': EN_DATA_SET.keys()})

        return context

    def post(self, request: ASGIRequest, *args, **kwargs):
        gpt_code = ''

        audio_file_obj = request.FILES.get('audio_data')

        # сохранить аудио локально (для тестов)
        # with open(f'app/static/app/audios/{audio_file_obj.name}', 'wb+') as file:
        #     for chunk in audio_file_obj.chunks():
        #         file.write(chunk)

        # вернуть аудио на фронт как оно есть (для тестов)
        # with open('app/static/app/audios/en_nums_test.wav', 'rb') as file:
        #     audio_file_obj = file.read()

        print(f'{"—"*50} START {"—"*50}')
        # вернуть аудио на фронт переозвученное другим голосом (для тестов)
        # audio_file_obj, gpt_code = recognize_text_from_audio_file('app/static/app/audios/ru_nums_test.wav')

        audio_file_obj, gpt_code = recognize_text_from_audio_file(audio_file_obj)
        print(f'{"—"*50} STOP {"—"*51}')

        # audio_file_obj = b'' # Заглушка

        if isinstance(audio_file_obj, InMemoryUploadedFile):
            audio_file_obj = audio_file_obj.read()

        base64_audio_data = b64encode(audio_file_obj).decode('utf-8')
        return JsonResponse({'audio_data': base64_audio_data, 'gpt_code': gpt_code})
