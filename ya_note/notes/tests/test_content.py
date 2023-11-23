from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestCommentEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note_author = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)
        cls.note_reader = Note.objects.create(
            title='Заголовок 2',
            text='Текст 2',
            author=cls.reader
        )

    def test_note_to_context(self):
        client = Client()
        client.force_login(self.author)
        response = client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        notes_in_context = response.context['object_list']
        self.assertIn(self.note_author, notes_in_context)

    def test_notes_of_different_user(self):
        client = Client()
        client.force_login(self.author)
        response = client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        notes_author = response.context['object_list']
        self.assertNotIn(self.note_reader, notes_author)

    def test_note_create_form(self):
        client = Client()
        client.force_login(self.author)
        response = client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteForm)
