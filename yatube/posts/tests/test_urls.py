from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='dnk',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

    def setUp(self):
        """Создаем клиент гостя, автора и зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.auth_user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTests.author)

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя."""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author}/',
            f'/posts/{self.post.pk}/',
        )
        for url in url_names:
            with self.subTest():
                response = self.client.get(url)
                error_name = (
                    f'Ошибка: нет доступа'
                    f'guest до страницы {url}'
                )
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name
                )

    def test_urls_response_auth(self):
        """Проверяем статус страниц для зарегистрированного пользователя."""
        url_status = {
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                error_name = (f'Ошибка: нет доступа auth_client'
                              f'до страницы {url}')
                self.assertEqual(response.status_code, status_code, error_name)

    def test_urls_response_guest_redirect(self):
        """Проверяем редирект страниц гостя."""
        pages = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/edit/':
            f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        }
        for page, value in pages.items():
            response = self.client.get(page)
            self.assertRedirects(response, value)

    def test_urls_response_not_author_redirect(self):
        """Проверяем редирект страниц пользователя не автора."""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, (
                f'/posts/{self.post.pk}/'
            )
        )

    def test_urls_uses_correct_template(self):
        """Проверяем, что адреса используют соответствующие шаблоны."""
        pages_adress = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html', }
        for address, template in pages_adress.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
