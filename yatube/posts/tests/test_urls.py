from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём двух пользователей
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_1 = User.objects.create_user(username='TestUser1')
        # Создаём группу
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создаём пост
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            id=999
        )
        cls.post = Post.objects.get(id=999)
        cls.group = Group.objects.get(slug='test-slug')

        cls.urls_template = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
            (f'/posts/{cls.post.id}/edit/', 'posts/post_create.html'),
            ('/create/', 'posts/post_create.html'),
        )

        cls.url_status = (
            ('/', HTTPStatus.OK.value),
            (f'/group/{cls.group.slug}/', HTTPStatus.OK.value),
            (f'/profile/{cls.user.username}/', HTTPStatus.OK.value),
            (f'/posts/{cls.post.pk}/', HTTPStatus.OK.value),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND.value),
        )

    def setUp(self):
        # Создаём клиент гостя и авторизуем наших пользователей
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(PostURLTests.user_1)

    def test_urls_exists_unauthorized(self):
        """Проверка доступности URL адресов"""
        for address, status in PostURLTests.url_status:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_exists_redirect_unauthorized(self):
        """Проверки редиректа неавторизованного пользователя"""
        response = self.guest_client.get('/posts/999/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/999/edit/'
        )
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_urls_exists_authorized(self):
        """
        Проверка доступности URL адреса '/create/'
        авторизированным пользователям
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_exists_post_author_not_author_edit(self):
        """
        Проверка доступности URL адреса '/edit/' автору поста
        и редиректа не автора
        """
        response = self.authorized_client1.get(
            '/posts/999/edit/', follow=True
        )
        response1 = self.authorized_client1.get(
            '/posts/999/edit/', follow=True
        )
        if PostURLTests.post.author.pk != PostURLTests.user.pk:
            self.assertRedirects(
                response1, '/auth/login/?next=/posts/999/edit/'
            )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        for address, template in PostURLTests.urls_template:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_comment_not_for_guest(self):
        """Комментарии недоступны гостям (редирект)"""
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostURLTests.post.pk})
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{PostURLTests.post.pk}/comment/'
        )
