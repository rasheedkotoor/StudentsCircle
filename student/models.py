from accounts.models import User
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.urls import reverse
from django.utils.text import slugify

# from .signals import delete_post_image , resize_post_image
from .utils import number, incrementor
from django.utils import timezone

# Create your models here.


def upload_post_to(instance, filename):
    return f'post_image/{instance.user.username}/{filename}'


class PostManager(models.Manager):
    def get_posts(self, status: bool = False):
        return (
            self.get_queryset()
            .select_related("user", "user__profile")
            .prefetch_related("likes__profile", "comment_set__user__profile")
            .filter(archived=status)
        )


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=False, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='post_images/', )
    # likes = models.ManyToManyField(User, related_name="likes", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} : {self.text[:10]}"

    @property
    def image_url(self):
        if self.image == '':
            image = ''
        else:
            image = self.image.url
        return image

    def save(self, *args, **kwargs):
        self.slug = slugify(self.text[:5] + str(number()))
        if not self.image:
            self.image = ""
        if not self.text:
            self.text = ""
        return super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]

    # to find url for each post
    def get_absolute_url(self):
        return reverse('student:detail', args=[self.slug])


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} : {self.user}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()


class SubComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    sub_com = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


# post_delete.connect(delete_post_image, sender=Post)
# post_save.connect(resize_post_image, sender=Post)
