from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём пользователя
        cls.user = User.objects.create_user(username='TestUser')
        # Создаём группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создаём пост
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        # Создаём авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Считаем кол-во постов в БД
        post_count = Post.objects.count()
        # Словарь для полей формы
        form_data = {
            'text': 'Новый текст',
            'group': PostFormTest.group.pk,
        }
        # POST-запрос для создания поста
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        # Проверка: изменилось ли кол-во постов (+1)
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверка: появился ли новый пост в БД
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        # Словарь для полей формы
        form_data = {
            'text': 'Изменённый текст',
            'group': PostFormTest.group.pk,
        }
        # POST-запрос для изменения поста
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostFormTest.post.pk
            }),
            data=form_data,
        )
        # Обновляем посты в БД
        PostFormTest.post.refresh_from_db()
        # Достаём изменённый пост из БД
        post_text = PostFormTest.post.text
        group = PostFormTest.post.pk
        # Проверки изменений текста поста и соответствие группы
        self.assertEqual(post_text, form_data['text'])
        self.assertEqual(group, form_data['group'])
