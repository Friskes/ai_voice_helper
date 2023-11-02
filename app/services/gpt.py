from __future__ import annotations

from string import punctuation
import re
from urllib.parse import urlparse, unquote

# https://github.com/xtekky/gpt4free
import g4f
g4f.logging = True # Отобразить какой провайдер используется
g4f.check_version = False # Отключить проверку версии при импорте


sym_replace_table = {
    '²': '2',
    '½': '1/2',
    '０': '0',
    '１': '1',
    '２': '2',
    '３': '3',
    '４': '4',
    '５': '5',
    '６': '6',
    '７': '7',
    '８': '8',
    '９': '9',
    ' ': ' ',
    '–': '-',
    '—': '-',
    '_': ' ',
    '«': '',
    '»': '',
    '`': ''
}
# sym_replace_table.update({sym: '' for sym in punctuation})
trans_table = str.maketrans(sym_replace_table)


def clear_text(answer: str) -> str:
    """Матрица замены символов в тексте для корректной озвучки"""

    return answer.translate(trans_table)


def check_answer(answer: str) -> tuple[str, str]:
    """Отделяем код от текста из ответа gpt.\n
    Модель 'gpt-3.5-turbo' помещает код в тройной апостроф.
    >>> ```print('example')```"""

    code = ''

    if '```' in answer:
        parts = answer.split('```')
        text = ''

        for i, part in enumerate(parts, 1):
            if i % 2 == 0:
                code += f'{part}\n'
            else:
                text += f'{part}\n'

        answer = text

    text = clear_text(answer)
    return text, code


def transform_links_from_text(text: str) -> str:
    """Удаляет/Преобразует ссылки в тексте в окончание ссылки."""

    # удалить текст типа: [цифра]
    text = re.sub(r'\[[0-9]+\]', '', text)
    # удалить ссылки типа: [Текст](Ссылка)
    text = re.sub(r"\[(.+)\]\(.+\)", '', text)
    # удалить двойные звездочки с обеих сторон слова типа: **Python**
    text = re.sub(
        r'(?<!\*\*)(\*\*([^*]*?[A-Za-z]+[^*]*?)\*\*)(?!\*\*)',
        lambda match: match.group(2),
        text
    )

    words = text.split()
    for i, word in enumerate(words):

        res = urlparse(word)
        link = re.findall(r'https?://[^,\s]+,?', res.path)

        if link:
            link = unquote(link[0])

            # text = text.replace(res.path, link.rsplit('/', 1)[-1])

            words[i] = link.rsplit('/', 1)[-1]
    text = ' '.join(words)

    return text


def get_gpt_answer(request_text: str) -> tuple[str, str]:
    """Получить ответ на вопрос от GPT"""

    answer, code = '', ''

    try:
        answer = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": request_text
            }],
            # provider=g4f.Provider.Aichat
        )

        # обработка ответа (проверка на наличие кода и очистка перед озвучкой)
        print(f'\n{"—"*21}Текст перед обработкой{"—"*20}\n{answer}\n{"—"*21}Текст перед обработкой{"—"*20}')
        answer, code = check_answer(answer)
        answer = transform_links_from_text(answer)
        print(f'\n{"—"*21}Текст после обработки{"—"*21}\n{answer}\n{"—"*21}Текст после обработки{"—"*21}')

    except Exception as exc:
        print('def get_gpt_answer:', exc)

    # обработаный текст возвращаем на озвучку
    return answer, code
