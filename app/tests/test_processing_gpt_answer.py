from django.test import TestCase

from app.services.gpt import transform_links_from_text, check_answer


# python manage.py test app.tests.test_processing_gpt_answer.TestProcessingGptAnswer
class TestProcessingGptAnswer(TestCase):

    @classmethod
    def setUpTestData(cls):

        file_names = (
            'ru_1.txt',
            'ru_2.txt',
            'ru_3.txt',
        )

        cls.texts = []
        for file_name in file_names:
            with open(f'app/static/app/texts/{file_name}', 'r', encoding='utf-8') as file:
                cls.texts.append(file.read())

    def test_processing(self):

        # for text in self.texts:
        for text in [self.texts[-1]]:
            print(f'\n{"~"*100}\n')
            text, code = check_answer(text)
            text = transform_links_from_text(text)
            print(text)
            print(f'\n{"~"*100}\n')
            print(code)
            print(f'\n{"~"*100}\n')
