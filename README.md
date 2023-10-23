## Голосовой помощник на Django, использующий нейронные сети для распознавания языка используемого в речи, распознавания речи в текст, генерации текстового ответа и синтеза текста в речь

### Установка проекта

#### Загрузите репозиторий с помощью команды:
`git clone https://github.com/Friskes/ai_voice_helper.git`

#### (Не обязательный шаг): Если у вас производительный компьютер с объёмом ОЗУ >= 24 вы можете скачать большие (large) модели vosk для более точного распознавания речи в текст по ссылкам ниже, а затем переместить их в директории как показано на схеме:

`https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip`
`https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip`

> (Примечание): Приложение автоматически загрузит легковесную малую (small) модель vosk при первом запуске, если не обнаружит большую (large) модель в директории проекта.

```
ai_voice_helper
│
├── app
│   ├── services
│   ├── static
│   │   └── app
│   │       ├── javascript
│   │       ├── models
│   │       │   ├── lang-id-voxlingua107-ecapa
│   │       │   ├── silero_models
│   │       │   ├── vosk_large
│   │       │   │   ├── en
│   │       │   │   │   └── <файлы/папки модели vosk-large-en>
│   │       │   │   └── ru
│   │       │   │       └── <файлы/папки модели vosk-large-ru>
│   │       │   └── vosk_small
│   │       └── styles
│   ├── templates
│   └── other files..
├── settings
└── other files..
```

#### Необходимо включить режим разработчика в Windows 10:
Параметры -> Обновление и безопасность -> Для разработчиков -> Режим разработчика (Вкл.)

#### Создайте виртуальное окружение:
`python -m venv venv`

#### Установите зависимости необходимые для работы проекта:
`pip install -r requirements.txt`

#### Сгенерируйте статические файлы:
`python manage.py collectstatic`

#### Выполните миграцию
`python manage.py migrate`

#### Для запуска проекта выполните команду:
`python manage.py runserver`

> (Примечание): Первый запуск проекта будет дольше обычного изза загрузки необходимых зависимостей.

#### Откройте в браузере проект по адресу:
`http://127.0.0.1:8000`

#### Для остановки программы нажмите сочетание клавиш CTRL+C
