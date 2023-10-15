## Голосовой ассистент на Django, использующий нейронные сети для распознавания речи в текст, генерации текстового ответа и синтеза текста в речь

### Установка проекта

#### Загрузите репозиторий с помощью команды:
`git clone https://github.com/Friskes/ai_voice_helper.git`

#### Скачайте ru, en модели silero, и ru модель vosk-small по ссылкам ниже, затем переместите их в директории как показано на схеме:
`https://models.silero.ai/models/tts/ru/v3_1_ru.pt`
`https://models.silero.ai/models/tts/en/v3_en.pt`
`https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip`
```
ai_voice_helper
│
├── app
│   ├── services
│   ├── static
│   │   └── app
│   │       ├── javascript
│   │       ├── models
│   │       │   ├── silero_models
│   │       │   │   ├── en
│   │       │   │   │   └── <файл модели silero en>
│   │       │   │   └── ru
│   │       │   │       └── <файл модели silero ru>
│   │       │   └── vosk_small
│   │       │       └── ru
│   │       │           └── <файлы модели vosk-small>
│   │       └── styles
│   ├── templates
│   └── other files..
├── settings
└── other files..
```

#### Создайте виртуальное окружение (необходим Python версии 3.8):
`py -3.8 -m venv venv`

#### Установите зависимости необходимые для работы проекта:
`pip install -r requirements.txt`

#### Сгенерируйте статические файлы:
`python manage.py collectstatic`

#### Выполните миграцию
`python manage.py migrate`

#### Для запуска проекта выполните команду:
`python manage.py runserver`

#### Откройте в браузере проект по адресу:
`http://127.0.0.1:8000`

#### Для остановки программы нажмите сочетание клавиш CTRL+C
