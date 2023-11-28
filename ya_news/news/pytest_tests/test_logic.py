import random
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author,
                                 form_data_comment, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data_comment)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data_comment['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data_comment, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data_comment)
    assert response.status_code == HTTPStatus.FOUND
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_word = random.choice(BAD_WORDS)
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assertFormError(response, 'form', 'text', errors=WARNING,)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_anonimous_user_cant_delete_comment_of_another_user(client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, form_data_comment,
                                 comment, news):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, form_data_comment)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data_comment['text']


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                form_data_comment, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, form_data_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text


@pytest.mark.django_db
def test_anonimous_user_cant_edit_comment_of_another_user(client,
                                                          form_data_comment,
                                                          comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = client.post(edit_url, form_data_comment)
    assert response.status_code == HTTPStatus.FOUND
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={edit_url}'
    assertRedirects(response, expected_url)
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
