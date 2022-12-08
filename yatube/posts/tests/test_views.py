from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(PostTests.auth_user)
        self.authorized_client_author.force_login(PostTests.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text = response.context.get('page_obj')[0].text
        post_author = response.context.get('page_obj')[0].author.username
        group_post = response.context.get('page_obj')[0].group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'TestAuthor')
        self.assertEqual(group_post, 'Тестовая группа')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        url = reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}
        )
        response = self.authorized_client.get(url)
        group_title = response.context.get('group').title
        group_description = response.context.get('group').description
        group_slug = response.context.get('group').slug
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_description, 'Тестовое описание')
        self.assertEqual(group_slug, 'test-slug')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        url = reverse('posts:profile', kwargs={'username': PostTests.author})
        response = self.authorized_client_author.get(url)
        post_text = response.context.get('page_obj')[0].text
        post_author = response.context.get('page_obj')[0].author.username
        group_post = response.context.get('page_obj')[0].group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'TestAuthor')
        self.assertEqual(group_post, 'Тестовая группа')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client_author.get(url)
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author.username
        group_post = response.context.get('post').group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'TestAuthor')
        self.assertEqual(group_post, 'Тестовая группа')

    def test_create_post_edit_show_correct_context(self):
        """Шаблон редактирования поста create_post сформирован
        с правильным контекстом."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client_author.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон создания поста create_post сформирован
        с правильным контекстом."""
        url = reverse('posts:post_create')
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_home_group_list_profile_pages(self):
        """Созданный пост отобразился на главной, на странице группы,
        в профиле пользователя."""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
        )
        for url in urls:
            response = self.authorized_client_author.get(url)
            self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_post_not_another_group(self):
        """Созданный пост не попал в группу, для которой не был предназначен"""
        another_group = Group.objects.create(
            title='Дополнительная тестовая группа',
            slug='test-another-slug',
            description='Тестовое описание дополнительной группы',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': another_group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                author=cls.author,
                text=f'Тестовый пост {i}',
                group=cls.group,
            )
            for i in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def test_first_page_contains_ten_records(self):
        """Количество постов на страницах index, group_list, profile
        равно 10."""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
        )
        for url in urls:
            response = self.client.get(url)
            amount_posts = len(response.context.get('page_obj').object_list)
            self.assertEqual(amount_posts, 10)

    def test_second_page_contains_three_records(self):
        """На страницах index, group_list, profile
        должно быть по три поста."""
        urls = (
            reverse('posts:index') + '?page=2',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2',
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ) + '?page=2',
        )
        for url in urls:
            response = self.client.get(url)
            amount_posts = len(response.context.get('page_obj').object_list)
            self.assertEqual(amount_posts, 3)
