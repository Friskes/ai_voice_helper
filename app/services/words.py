# Тренировочная модель для матрицы ИИ
# Первое слово в значении - имя функции для запуска команды.
RU_DATA_SET = {
    'скажи число пи': 'pi не скажу',

    'о чём ты думаешь': 'thinking обдумываю алгоритмы',

    'кем ты видишь себя через пять лет': 'five_years отмечающей годовщину порабощения человечества',
}

EN_DATA_SET = {
    'say the number pi': 'pi I wont tell',

    'what are you thinking about': 'thinking thinking about algorithms',

    'who do you see yourself in five years': 'five_years celebrating the anniversary of the enslavement of humanity',
}

RU_ANSWERS = (
    'Я не поняла',
    'Не смогла разобрать повтори ещё раз пожалуйста',
    'Не расслышала',
    'Повтори ещё один раз пожалуйста',
    'Повтори',
    'Скажи ещё раз'
)

EN_ANSWERS = (
    'I didnt understand',
    'I couldnt make it out please repeat it again',
    'I didnt hear you',
    'Repeat it one more time please',
    'Repeat',
    'Say it again'
)

NOT_UNDERSTAND_ANSWERS = {'ru': RU_ANSWERS, 'en': EN_ANSWERS}
