from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    """Создаем тестовые посты, группу и форму."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='prosaics',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Вывожу тестовый пост',
            group=cls.group,
        )

    @classmethod
    def setUp(cls):
        """Создаем клиент зарегистрированного пользователя."""
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Вывожу тестовый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.user.username}
        ))
        post_ = PostFormTests.post
        objects_names = {
            post_.group: post.group,
            post_.author: post.author,
            post_.text: post.text,
        }
        for object_, value in objects_names.items():
            with self.subTest(object_=object_):
                self.assertEqual(object_, value)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Форма редактирует запись в Post."""
        form_data = {
            'text': 'Измененный старый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
        )
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk}
        ))
        objects_names = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
        }
        for object_, value in objects_names.items():
            with self.subTest(object_=object_):
                self.assertEqual(object_, value)
