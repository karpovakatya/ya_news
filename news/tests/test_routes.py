from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс модели новостей.
from news.models import Comment, News

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём объект для теста
        # Добавляем фикстуру с созданием первой новости:
        cls.news = News.objects.create(title='Заголовок', text='Текст')

        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    # def test_home_page(self):
    #     # Вызываем метод get для клиента (self.client)
    #     # и загружаем главную страницу.
    #     url = reverse('news:home')
    #     # response = self.client.get('/')
    #     response = self.client.get(url)
    #     # Проверяем, что код ответа равен 200 OK.
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # # Получаем адрес страницы для запроса
    # # path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail')
    # # Адресом страницы с новостью, созданной в фикстуре, будет /news/1/: 
    # # нам точно известно, что это первый объект, который создан в пустой таблице БД.
    # def test_detail_page(self):
    #     url = reverse('news:detail', args=(self.news.id,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    '''
    Проверяем доступность страниц для анонимных пользователей.
    '''
    def test_pages_availability(self):
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов, 
            # поэтому вторым параметром ставим None.
            ('news:home', None),  # главная
            # Путь для страницы новости
            # принимает в качестве позиционного аргумента
            # id записи; передаём его в кортеже.
            ('news:detail', (self.news.id,)),  # страница новости
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        # Итерируемся по внешнему кортежу
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Эти проверки можно записать в виде subTest() на четыре строки,
    # но Напишем код иначе: через вложенные циклы.
    def test_availability_for_comment_edit_and_delete(self):
        # вложенные кортежи будут содержать объект пользователя и ответ,
        # который ожидается при обращении к страницам редактирования и удаления комментария
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # При тестировании редиректа применяйте метод 'assertRedirects' из 'django.test'

    # Для двух страниц нужно провести одинаковые тесты — применим subTest()
    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования/удаления комментария:
                url = reverse(name, args=(self.comment.id,))
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'  # ОР
                response = self.client.get(url)  # ФР
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                # ФР сравниваем с ОР
                self.assertRedirects(response, redirect_url)
