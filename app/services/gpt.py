from __future__ import annotations
from string import punctuation

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
    '«': '',
    '»': ''
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



def get_gpt_answer(request_text: str) -> tuple[str, str]:
    """Получить ответ на вопрос от GPT"""

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
        # print('\nBEFORE: ', answer, end='\n\n')
        answer, code = check_answer(answer)
        # print('AFTER: ', answer, end='\n\n')

    except Exception as exc:
        print('def get_gpt_answer:', exc)
        answer, code = '', ''

    # обработаный текст возвращаем на озвучку
    return answer, code
