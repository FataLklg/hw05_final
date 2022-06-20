from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser')

        cls.template_name_pages = (
            (reverse('about:author'), 'about/author.html'),
            (reverse('about:tech'), 'about/tech.html'),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(AboutURLTests.user)

    def test_template_namespace(self):
        """Проверка имени путей в urls"""
        for reverse_name, template in AboutURLTests.template_name_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
