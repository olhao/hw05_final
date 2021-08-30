import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    post_text = "Тестовый текст"
    post_author = "auth"
    post_group = "Тестовая группа"
    group_description = "Тестовое описание"
    image = "posts/small.gif"
    comment_text = "Текст комментария"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post_user = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
            image=uploaded,
        )
        cls.comment_user = Comment.objects.create(
            post=cls.post_user,
            author=cls.user,
            text="Текст комментария",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "posts/create_post.html": reverse("posts:post_create"),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": str(self.post_user.pk)}
            ),
            "posts/profile.html": reverse("posts:profile",
                                          kwargs={"username": "auth"}),
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ),
            "posts/index.html": reverse("posts:index"),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_page_uses_correct_template(self):
        response = self.authorized_client.get(
            reverse("posts:post_edit",
                    kwargs={"post_id": str(self.post_user.pk)})
        )
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_home_page_show_correct_context(self):
        response = self.guest_client.get(reverse("posts:index"))

        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image

        self.assertEqual(post_text_0, self.post_text)
        self.assertEqual(post_author_0, self.post_author)
        self.assertEqual(post_group_0, self.post_group)
        self.assertEqual(post_image_0, self.image)

    def test_posts_group_list_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )

        self.assertEqual(response.context.get("group").title, self.post_group)
        self.assertEqual(
            response.context.get("group").description, self.group_description
        )

        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image

        self.assertEqual(post_text_0, self.post_text)
        self.assertEqual(post_author_0, self.post_author)
        self.assertEqual(post_group_0, self.post_group)
        self.assertEqual(post_image_0, self.image)

    def test_profile_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )

        self.assertEqual(response.context.get("author").username,
                         self.post_author)

        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image

        self.assertEqual(post_text_0, self.post_text)
        self.assertEqual(post_author_0, self.post_author)
        self.assertEqual(post_group_0, self.post_group)
        self.assertEqual(post_image_0, self.image)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post_user.pk})
        )

        # self.assertEqual(response.context.get('post').text, self.post_text)

        post_object = response.context["post"]
        post_text = post_object.text
        post_author = post_object.author.username
        post_group = post_object.group.title
        post_image = post_object.image

        self.assertEqual(post_text, self.post_text)
        self.assertEqual(post_author, self.post_author)
        self.assertEqual(post_group, self.post_group)
        self.assertEqual(post_image, self.image)

    def test_post_create_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))

        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post_user.pk})
        )

        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post_user.pk})
        )

        first_object = response.context["comments"][0]
        comment_0 = first_object.text
        self.assertEqual(comment_0, self.comment_text)


class PaginatorViewsTest(TestCase):
    ten_posts = 10
    three_posts = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )

        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text="Тестовый текст" + str(i),
                group=cls.group,
            )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_home_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), self.ten_posts)

    def test_second_home_page_contains_three_records(self):
        response = self.authorized_client.get(reverse
                                              ("posts:index")
                                              + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), self.three_posts)

    def test_first_group_list_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), self.ten_posts)

    def test_second_group_list_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse("posts:group_list",
                    kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), self.three_posts)

    def test_first_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(len(response.context["page_obj"]), self.ten_posts)

    def test_second_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "auth"}) + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), self.three_posts)


class PostIntegrationViewsTests(TestCase):
    post_text = "Тестовый текст"
    post_group_1 = "Тестовая группа 1"
    post_group_2 = "Тестовая группа 2"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")

        cls.group = Group.objects.create(
            title="Тестовая группа 1",
            slug="test-slug-1",
            description="Тестовое описание 1",
        )
        cls.group_second = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug-2",
            description="Тестовое описание 2",
        )
        cls.post_user = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_group_test_of_created_post(self):
        response_index = self.authorized_client.get(reverse("posts:index"))
        response_group = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug-1"})
        )
        response_profile = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(response_index.context["page_obj"][0].text,
                         self.post_text)
        self.assertEqual(
            response_index.context["page_obj"][0].group.title,
            self.post_group_1
        )
        self.assertIsNot(
            response_index.context["page_obj"][0].group.title,
            self.post_group_2
        )
        self.assertEqual(response_group.context["page_obj"][0].text,
                         self.post_text)
        self.assertEqual(response_profile.context["page_obj"][0].text,
                         self.post_text)


class PostCacheIndexViewTests(TestCase):
    post_text = "Тестовый текст"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")

        cls.post_user = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_of_home_page(self):
        response_post_exits = self.guest_client.get(reverse
                                                    ("posts:index"))\
            .content
        self.post_user.delete()
        response_post_deleted = self.guest_client.get(reverse
                                                      ("posts:index"))\
            .content
        self.assertEqual(response_post_exits, response_post_deleted)
        cache.clear()
        response_cache_cleared = self.guest_client.get(reverse
                                                       ("posts:index"))\
            .content
        self.assertNotEqual(response_post_exits, response_cache_cleared)


class PostFollowViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username="follower")
        cls.user2 = User.objects.create_user(username="not_follower")
        cls.user3 = User.objects.create_user(username="following")

        cls.post_following = Post.objects.create(
            author=cls.user3,
            text="Тестовый пост",
        )

    def setUp(self) -> None:
        self.follower = Client()
        self.follower.force_login(self.user1)
        self.not_follower = Client()
        self.not_follower.force_login(self.user2)
        self.following = Client()
        self.following.force_login(self.user3)

    def test_follow_and_unfollow_the_user(self):
        follow = Follow.objects.create(user=self.user1, author=self.user3)
        self.assertTrue(follow, "Пользователь не подписан")
        unfollow = follow.delete()
        self.assertTrue(unfollow, "Пользователь не отписался")

    def test_following_post_visibility(self):
        content_before_follow = self.follower.get(reverse
                                                  ("posts:follow_index"))\
            .content
        Follow.objects.create(user=self.user1, author=self.user3)
        content_after_follow = self.follower.get(reverse
                                                 ("posts:follow_index"))\
            .content
        content_for_not_follower = self.not_follower.get(
            reverse("posts:follow_index")
        ).content
        self.assertNotEqual(
            content_before_follow,
            content_after_follow,
            "Пост автора, на которого была оформлена подписка отсутствует",
        )

        self.assertNotEqual(
            content_after_follow,
            content_for_not_follower,
            "Пост отображается на странице подписок, "
            "для неподписанного автора",
        )
