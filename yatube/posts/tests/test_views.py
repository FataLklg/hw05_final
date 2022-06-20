import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.user_3 = User.objects.create_user(username='TestUser3')
        # Создаём группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Создаём 15 постов
        posts_list = []
        for i in range(15):
            posts_list.append(
                Post(
                    text=f'Тестовый текст{i}',
                    author=cls.user,
                    group=cls.group,
                    image=cls.uploaded
                )
            )
        Post.objects.bulk_create(posts_list)
        cls.post = Post.objects.all()
        cls.comment = Comment.objects.all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаём гостя и авторизированного клиента
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostViewsTests.user_2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(PostViewsTests.user_3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): (
                'posts/index.html'
            ),
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTests.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile',
                    kwargs={'username': PostViewsTests.user}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTests.post[0].pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewsTests.post[0].pk}): (
                'posts/post_create.html'
            ),
            reverse('posts:post_create'): (
                'posts/post_create.html'
            ),
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context, 'Не найден')
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post[0].text)
        self.assertEqual(post_author_0, PostViewsTests.user)
        self.assertEqual(post_image_0, PostViewsTests.post[0].image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTests.group.slug})
        )
        self.assertIn('page_obj', response.context, 'Не найден')
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post[0].text)
        self.assertEqual(post_author_0, PostViewsTests.post[0].author)
        self.assertEqual(post_image_0, PostViewsTests.post[0].image)
        self.assertIn('group', response.context, 'Не найден')
        post_group = response.context['group']
        self.assertEqual(post_group, PostViewsTests.post[0].group)

    def test_post_group_on_page_another_group(self):
        """Не попал ли пост одной группы на страницу другой"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group1.slug})
        )
        self.assertIn('page_obj', response.context, 'Не найден')
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': PostViewsTests.user})
        )
        self.assertIn('page_obj', response.context, 'Не найден')
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostViewsTests.post[0].text)
        self.assertEqual(post_author_0, PostViewsTests.post[0].author)
        self.assertEqual(post_image_0, PostViewsTests.post[0].image)
        self.assertIn('username', response.context, 'Не найден')
        username = response.context['username']
        self.assertEqual(username, PostViewsTests.user)
        self.assertIn('profile_posts', response.context, 'Не найден')
        profile_posts = response.context['profile_posts'][0].text
        self.assertEqual(profile_posts, PostViewsTests.post[0].text)
        self.assertIn('count_posts', response.context, 'Не найден')
        posts_count = response.context['count_posts']
        self.assertEqual(posts_count, PostViewsTests.post.count())

    def test_paginator_correct_working(self):
        """Проверка паджинации страниц"""
        # Словарь с запросом url первых страниц
        paginator_pages_1 = {
            'index_response_1': self.authorized_client.get(
                reverse('posts:index')),
            'group_list_response_1': self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': PostViewsTests.group.slug})
            ),
            'profile_response_1': self.authorized_client.get(
                reverse('posts:profile',
                        kwargs={'username': PostViewsTests.user})
            ),
        }
        # Словарь с запросом url вторых страниц
        paginator_pages_2 = {
            'index_response_2': self.guest_client.get(
                reverse('posts:index') + '?page=2'
            ),
            'group_list_response_2': self.guest_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': PostViewsTests.group.slug}) + '?page=2'
            ),
            'profile_response_2': self.guest_client.get(
                reverse('posts:profile',
                        kwargs={'username': PostViewsTests.user}) + '?page=2'
            ),
        }
        # Перебор словарей на наличие ожидаемого кол-ва записей
        for page_name, response in paginator_pages_1.items():
            with self.subTest(page_name=page_name):
                self.assertIn('page_obj', response.context, 'Не найден')
                self.assertEqual(len(response.context['page_obj']), 10)
        for page_name, response in paginator_pages_2.items():
            with self.subTest(page_name=page_name):
                self.assertIn('page_obj', response.context, 'Не найден')
                self.assertEqual(len(response.context['page_obj']), 5)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTests.post[0].id})
        )
        self.assertIn('post', response.context, 'Не найден')
        post = response.context['post']
        post_text = post.text
        post_author = post.author
        post_image_0 = post.image
        self.assertEqual(post_text, PostViewsTests.post[0].text)
        self.assertEqual(post_author, PostViewsTests.post[0].author)
        self.assertEqual(post_image_0, PostViewsTests.post[0].image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('form', response.context, 'Не найден')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_edit_page_show_correct_context(self):
        """Шаблон post_create(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewsTests.post[0].id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('form', response.context, 'Не найден')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_add_comment_show_correct_on_post_page(self):
        """Добавленный комментарий отображается на странице поста."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': PostViewsTests.post[0].id
            }),
            data=form_data,
        )
        # Проверка: изменилось ли кол-во комментариев (+1)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверка: появился ли новый комментарий в БД
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists())

    def test_index_page_cache_work_correct(self):
        """Кэширование постов на главной странице."""
        post = Post.objects.create(
            text='Test cache', author=PostViewsTests.user
        )
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        post.delete()
        response2 = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response2.content)

    def test_user_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться и отписываться"""
        self.authorized_client2.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTests.user}
            )
        )
        # Появился ли новый объект модели Follow
        self.assertTrue(
            Follow.objects.filter(
                author=PostViewsTests.user,
            ).exists())
        self.authorized_client2.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTests.user}
            )
        )
        print(PostViewsTests.user_2.follower.filter(author=PostViewsTests.user))
        response = self.authorized_client2.get(
            reverse(
                'posts:follow_index'
            )
        )
        context_user2 = response.context['page_obj']
        post_text_0 = context_user2[0].text
        self.assertIn('page_obj', response.context, 'Не найден')
        # Проверка соответствия текста поста подписки с текстом поста автора
        self.assertEqual(post_text_0, PostViewsTests.post[0].text)
        response_unfollow = self.authorized_client3.get(
            reverse(
                'posts:follow_index'
            )
        )
        context_user3 = response_unfollow.context['page_obj']
        # Сравнение контекста подписанного/неподписанного пользователя
        self.assertNotEqual(context_user2, context_user3)
        follow_count_before = Follow.objects.count()
        self.authorized_client2.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostViewsTests.user}
            )
        )
        follow_count_after = Follow.objects.count()
        # Сравниваем кол-во объектов модели Follow до и после отписки
        self.assertEqual(follow_count_after, follow_count_before - 1)
