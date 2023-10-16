import pytest
from datetime import datetime, timedelta
from django.utils import timezone
# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment
from django.conf import settings


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    """Создаем пользователя с ролью автора комментария"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    """Создали клиента, авторизованного под автором"""
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    """Создаем объект новости"""
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def ten_news():
    """Создаем 10 новостей"""
    today = datetime.today()
    ten_news = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return ten_news


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания новости.
def id_for_args(news):
    # И возвращает кортеж, который содержит id новости.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return news.id,


@pytest.fixture
def comment(author, news):
    """Создаем объект комментария"""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания комментария.
def id_for_args_comment(comment):
    return comment.id,


@pytest.fixture
def some_comments(author, news):
    """Фикстура создает несколько комментариев"""
    # Запоминаем текущее время:
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author,
            text=f'Прокомментировал {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
