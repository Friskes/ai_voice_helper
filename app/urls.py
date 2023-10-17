from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from app.views import AiVoiceHelperView


urlpatterns = [
    path('favicon.ico/', 
        RedirectView.as_view(url=staticfiles_storage.url('app/images/favicon.ico'), permanent=True), 
        name='favicon'
    ),

    path('', AiVoiceHelperView.as_view(), name='ai_voice_helper')
]
