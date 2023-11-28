from http import HTTPStatus

import pytils.translit
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add',)
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'test_slug',
            'author': cls.author,
        }
        cls.notes = Note.objects.create(
            title='Test title',
            text='Test text',
            slug='test',
            author=cls.author
        )

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/done/')
        note_exists = Note.objects.filter(title='Заголовок').exists()
        self.assertTrue(note_exists)
        created_note = Note.objects.get(title='Заголовок')
        self.assertEqual(created_note.text, 'Текст')
        self.assertEqual(created_note.slug, 'test_slug')
        self.assertEqual(created_note.author, self.author)

    def test_user_cant_use_same_slug(self):
        same_slug = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'slug': 'test',
            'author': self.author,
        }
        response = self.auth_client.post(self.url, data=same_slug)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(f'{same_slug["slug"]}' + WARNING)
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_automatic_slug_creation(self):
        empty_slug = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'author': self.author,
        }
        response = self.auth_client.post(self.url, data=empty_slug)
        self.assertRedirects(response, '/done/')
        created_note = Note.objects.get(title='Тестовый заголовок')
        expected_slug = pytils.translit.slugify(empty_slug['title'])
        self.assertEqual(created_note.slug, expected_slug)


class TestCommentEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testauthor')
        cls.reader = User.objects.create(username='testreader')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_notes_availability_for_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse('notes:detail', args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
