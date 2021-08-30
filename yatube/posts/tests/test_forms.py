import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Post, User

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    post_text_new = "Текст для теста test_new_post_created_in_database"
    post_text_edited = "Отредактированный текст"
    post_author = "auth"
    image = "posts/small.gif"
    comment_text = "Текст комментария"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_post_created_in_database(self):
        posts_count = Post.objects.count()

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

        form_data = {
            "text": "Текст для теста test_new_post_created_in_database",
            "image": uploaded,
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, self.post_text_new)
        self.assertEqual(post.author.username, self.post_author)
        self.assertEqual(post.group, None)
        self.assertTrue(
            Post.objects.filter(text=self.post_text_new, image=self.image)
                .exists()
        )

    def test_new_post_not_created_in_database(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Текст для теста test_new_post_not_created_in_database"}
        response = self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse("users:login")
                             + "?next="
                             + reverse("posts:post_create"))

        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edited_in_database(self):
        post_id = self.post.pk
        form_data_edited = {
            "text": "Отредактированный текст",
        }
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data_edited,
            follow=True,
        )
        post = Post.objects.first()
        self.assertTrue(Post.objects.filter(text=form_data_edited.get("text"))
                        .exists())
        self.assertEqual(post.text, self.post_text_edited)
        self.assertEqual(post.author.username, self.post_author)

    def test_new_comment_created_in_database(self):
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_comment = {"text": "Текст комментария"}
        self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post_id}),
            data=form_comment,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, self.comment_text)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def text_new_comment_not_created_in_database(self):
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_comment = {
            "text": "Текст комментария",
        }
        self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post_id}),
            data=form_comment,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)
