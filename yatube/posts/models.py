from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        "Группа", max_length=200, help_text="Добавьте название группы"
    )
    slug = models.SlugField("Слаг", unique=True, help_text="Добавьте слаг")
    description = models.TextField("Описание", help_text="Добавьте описание")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    text = models.TextField("Текст поста",
                            blank=False,
                            help_text="Введите тест поста")
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
        help_text="Добавьте дату публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        help_text="Впишите имя автора поста",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу",
    )

    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
        help_text="Добавьте комментарий к посту",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
        help_text="Впишите имя автора комментария",
    )

    text = models.TextField(
        "Текст комментария", blank=False, help_text="Введите тест комментария"
    )

    created = models.DateTimeField(
        "Дата комментария",
        auto_now_add=True,
        help_text="Добавьте дату коментария"
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-created"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    #  кто подписывается
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
        help_text="Впишите имя пользователя",
    )
    #  на кого подписываются
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Впишите имя автора",
        null=True,
    )

    def __str__(self):
        return str(self.author)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
