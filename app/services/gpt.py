from __future__ import annotations

# https://github.com/xtekky/gpt4free
import g4f
g4f.logging = True # Отобразить какой провайдер используется
g4f.check_version = False # Отключить проверку версии при импорте

from string import punctuation


other_symbols = r'²½０１２３４５６７８９'

table = str.maketrans({
    sym: '' for sym in punctuation + other_symbols
    # '`': '',
    # '(': '',
    # ')': ' ',
    # '@': 'at ',
    # '_': ' '
})


def clear_text(text: str) -> str:
    """Матрица замены символов в тексте для корректной озвучки"""

    return text.translate(table)


def check_answer(answer: str) -> tuple[str, str]:
    """Отделяем код от текста из ответа gpt.\n
    Модель 'gpt-3.5-turbo' помещает код в тройной апостроф.
    >>> ```print('example')```"""

    code = ''

    if '```' in answer:
        parts = answer.split('```')
        text = ''

        count = 1
        for i in parts:
            if count % 2 == 0:
                code += f'{i} \n'
            else:
                text += f'{i} \n'
            count += 1

        answer = text

    text = clear_text(answer)
    return text, code


def get_gpt_answer(question: str) -> tuple[str, str]:
    """Получить ответ на вопрос от GPT"""

    try:
        answer = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": question
            }],
            # provider=g4f.Provider.Aichat
        )
        # обработка ответа (проверка на наличие кода и очистка перед озвучкой)
        # print('\nBEFORE: ', answer, end='\n\n')
        answer, code = check_answer(answer)
        # print('AFTER: ', answer, end='\n\n')

    except Exception as exc:
        print('def get_gpt_answer:', exc)
        answer, code = '', ''

    # обработаный текст возвращаем на озвучку
    return answer, code
