from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём пользователя
        cls.user = User.objects.create_user(username='auth')
        # Создаём группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        # Создаём пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        """verbose_name в полях моделей Post и Group совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        post_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        group_verboses = {
            'title': 'Название группы',
            'slug': 'Фрагмент URL',
            'description': 'Описание',
        }
        # Проверка verbose_name полей поста
        for field, expected_value in post_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
        # Проверка verbose_name полей группы
        for field, expected_value in group_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях моделей Post и Group совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        post_help_texts = {
            'text': 'Поле для ввода текста поста',
            'author': 'Указание автора поста',
            'group': 'Выбор группы, к которой относится пост',
        }
        group_help_texts = {
            'title': 'Укажите желаемое название группы',
            'slug': 'Часть маршрута URL адреса группы',
            'description': 'Короткое описание группы',
        }
        # Проверка help_text полей поста
        for field, expected_value in post_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
        # Проверка help_text полей группы
        for field, expected_value in group_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
