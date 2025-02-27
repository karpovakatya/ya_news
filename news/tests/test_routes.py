from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Comment, News

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

    '''
    Проверяем доступность редактирования и удаления комментариев
    для автора и не-автора.
    '''
    # Эти проверки можно записать в виде subTest() на четыре строки,
    # но Напишем код иначе: через вложенные циклы.
    def test_availability_for_comment_edit_and_delete(self):
        # вложенные кортежи будут содержать объект пользователя и ответ,
        # который ожидается при обращении к страницам редактирования
        # и удаления комментария
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

    '''
    Проверяем редиректы для анонимных пользователей.
    '''
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
                redirect_url = f'{login_url}?next={url}'  # ОР
                response = self.client.get(url)  # ФР
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                # ФР сравниваем с ОР
                self.assertRedirects(response, redirect_url)
