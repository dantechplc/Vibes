from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from pilkit.processors import ResizeToFill
from taggit.managers import TaggableManager
from account.models import Author, Account
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .signals import object_viewed_signal

User = get_user_model()


class MostViewedManager(models.Manager):

    def most_read_posts(self):
        history = Post.objects.annotate(highest_view=Count('views')).order_by('-views')[:5]

        return history


class Category(models.Model):
    title = models.CharField(_("Title"), max_length=50)
    cover_picture = models.ImageField(
        _("Thumbnail"), upload_to="category/thumbnail", blank=True, null=True,
    )
    cover_picture_thumbnail = ImageSpecField(source='cover_picture',
                                             processors=[ResizeToFill(391, 101)],
                                             format="PNG",
                                             options={'quality': 80})

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title

    def get_post_count(self):
        post = Post.objects.filter(category=self.id).count()
        return post


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(_("Title"), max_length=100)
    overview = RichTextField(_("Overview"), default="")
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    content = RichTextUploadingField(blank=True, null=True,
                                     external_plugin_resources=[('youtube',
                                                                 '/mediafiles/ckeditor/ckeditor/plugins/youtube/',
                                                                 'plugin.js')])
    featured = models.BooleanField(_("Featured"), default=False)
    category = models.ForeignKey(
        Category, null=True, verbose_name=_("Category"), related_name="post", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        Author, verbose_name=_("Author"), on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    cover_picture = models.ImageField(
        _("Thumbnail"), upload_to="post/thumbnail", blank=True, null=True,
    )
    cover_picture_thumbnail = ImageSpecField(source='cover_picture',
                                             processors=[ResizeToFill(900, 631)],
                                             format="JPEG",
                                             options={'quality': 80})
    slug = models.SlugField(_("Slug"), blank=True, null=True)
    tags = TaggableManager()
    most_read_posts = MostViewedManager()
    objects = models.Manager()
    favourites = models.ManyToManyField(
        Account, related_name='favourite', default=None, blank=True)
    likes = models.ManyToManyField(Account, blank=True, related_name="likes")
    views = models.PositiveIntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Absolute URL for Post"""
        return reverse('post_detail', kwargs={"slug": self.slug})

    def get_update_url(self):
        """Update URL for Post"""
        return reverse("post_update", kwargs={"slug": self.slug})

    def get_delete_url(self):
        """Delete URL for Post"""
        return reverse("post_delete", kwargs={"slug": self.slug})

    def get_comments(self):
        return self.comments.filter(parent=None).filter(status=True)

    def get_total_views(self):
        count = History.objects.filter(object_id=self.id).count()
        most_read_posts = Post.objects.filter(id=self.id)
        most_read_posts.update(views=count)
        self.views = count
        return self.views

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title + '-' + str(self.id))
        self.views = self.get_total_views()
        super().save(*args, **kwargs)


class Comment(MPTTModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    user = models.ForeignKey(Account, blank=True, null=True, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')

    content = models.TextField(null=True)
    # publish = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.BooleanField(default=True, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['status']

    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)

    def __str__(self):
        return str(self.post) + " --- " + str(self.user)


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    viewed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s viewed: %s" % (self.content_object, self.viewed)

    class Meta:
        verbose_name_plural = "Histories"


def object_viewed_recevier(sender, instance, request, *args, **kwargs):
    if History.objects.filter(user=request.user, object_id=instance.id).exists():
        return None
    else:
        new_history = History.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.id
        )


object_viewed_signal.connect(object_viewed_recevier)
