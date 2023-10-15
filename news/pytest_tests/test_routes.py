import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:logout', None),
    ),
)
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, name, args):
    """Анонимному пользователю доступны страницы:
    главная, страницы регистрации, входа и выхода."""

    url = reverse(name, args=args)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'args',
    (pytest.lazy_fixture('id_for_args_comment'),),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_status, name, args
):
    """Пользователь авторизован.

    Проверяем доступность комментария для автора
    и недоступность для не-автора (ошибка 404)."""

    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.parametrize(
    'args',
    (pytest.lazy_fixture('id_for_args_comment'),),
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
