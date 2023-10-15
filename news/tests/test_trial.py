from news.models import News
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

# Получаем модель пользователя.
User = get_user_model()


class TestNews(TestCase):
    # Все нужные переменные сохраняем в атрибуты класса.
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            # При создании объекта обращаемся к константам класса через cls.
            title=cls.TITLE,
            text=cls.TEXT,
        )

        # Создаём пользователя.
        cls.user = User.objects.create(username='testUser')
        # Создаём объект клиента.
        cls.user_client = Client()
        # "Логинимся" в клиенте при помощи метода force_login()
        cls.user_client.force_login(cls.user)
        # Теперь через этот клиент можно отправлять запросы
        # от имени пользователя с логином "testUser".

    def test_successful_creation(self):
        news_count = News.objects.count()
        self.assertEqual(news_count, 1)

    def test_title(self):
        # Чтобы проверить равенство с константой -
        # обращаемся к ней через self, а не через cls:
        self.assertEqual(self.news.title, self.TITLE)

# групповое создание объектов


'''
    @classmethod
    def setUpTestData(cls):
        all_news = []
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(title=f'Новость {index}', text='Просто текст.')
            all_news.append(news)
        News.objects.bulk_create(all_news)
'''

''' Тот же результат можно получить при помощи list comprehension
    @classmethod
    def setUpTestData(cls):
        all_news = [
            News(title=f'Новость {index}', text='Просто текст.')
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)
'''

''' А можно написать выражение, создающее объекты новостей внутри bulk_create():
    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create(
            News(title=f'Новость {index}', text='Просто текст.')
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )
'''

'''
# Вместо ключа с именем модели (news_list, в нашем примере) можно задать и любой другой ключ 
при помощи атрибута context_object_name в Class-Based View. Например, вот так:
Затем имя news_feed можно применять в тестах и в шаблонах.

class NewsList(generic.ListView):
    """Список новостей."""
    model = News
    template_name = 'news/home.html'
    context_object_name = 'news_feed'
'''

'''
from datetime import datetime, timedelta

# Текущая дата.
today = datetime.today()
# Вчера.
yesterday = today - timedelta(days=1)
# Завтра.
tomorrow = today + timedelta(days=1)
'''
