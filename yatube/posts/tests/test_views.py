from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    """Создаем тестовые посты и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='leo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='prosaics',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                'Грусть моя, как пленная сербка, '
                'Родной произносит свой толк. '
                'Напевному слову так терпко '
                'В устах, целовавших твой шелк.'
            ),
            group=cls.group,
        )

    def test_views_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html'}
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_paginator_correct_context(self):
        """Шаблоны index, group_list и profile отображаются правильно"""
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostViewTests.user,
                text=f'Тестовый пост {i}',
                group=PostViewTests.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']), 10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']), 8
                )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response_index = self.authorized_client.get(
            reverse('posts:index')
        )
        task_group = response_index.context['page_obj'][0]
        self.assertEqual(task_group, self.post)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug})
        )
        task_post = response_group_list.context['page_obj'][0]
        task_group = response_group_list.context['group']
        self.assertEqual(task_post, self.post)
        self.assertEqual(task_group, self.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        response_post = response_post_detail.context['post']
        self.assertEqual(response_post, self.post)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author})
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)
        self.assertEqual(response.context['author'], self.post.author)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertIsNone(response.context.get('is_edit', None))

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertTrue(response.context['is_edit'])
                self.assertIsInstance(response.context['is_edit'], bool)
