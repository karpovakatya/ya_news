import pytest

# from http import HTTPStatus
from django.conf import settings
from django.urls import reverse

HOME_URL = reverse("news:home")


@pytest.mark.django_db
def test_news_count(client, ten_news):
    """Проверяем количество новостей на главной."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, ten_news):
    """Проверяем сортировку новостей на главной."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, id_for_args, some_comments):
    """Тестируем сортировку комментариев на странице новости."""
    detail_url = reverse('news:detail', args=id_for_args)
    response = client.get(detail_url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости из контекста.
    context_news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = context_news.comment_set.all()
    # Проверяем, что время создания первого комментария в списке
    # меньше, чем время создания второго.
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, comment_form_available',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_has_comment_form(
    id_for_args,
    parametrized_client,
    comment_form_available
):
    detail_url = reverse('news:detail', args=id_for_args)
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is comment_form_available
