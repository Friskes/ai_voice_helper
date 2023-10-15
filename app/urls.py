from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from app.views import AssistantView


urlpatterns = [
    path('favicon.ico/', 
        RedirectView.as_view(url=staticfiles_storage.url('app/images/favicon.ico'), permanent=True), 
        name='favicon'
    ),

    path('', AssistantView.as_view(), name='assistant')
]
