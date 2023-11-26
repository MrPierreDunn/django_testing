from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, setup_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, setup_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    sorted_object_list = sorted(object_list, key=lambda news: news.date, reverse=True)
    assert list(object_list) == sorted_object_list


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context


@pytest.mark.django_db
def test_comments_order(client, news, setup_comment):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = sorted(all_comments,
                             key=lambda comment: comment.created,
                             reverse=False)
    assert sorted_comments == list(all_comments)
