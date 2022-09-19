from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from django.utils.translation import ugettext_lazy as _
from .constants import *
# Create your models here.
from pilkit.processors import ResizeToFill


class User(AbstractUser):
    username = models.CharField(_('username'), unique=False, max_length=100)
    email = models.EmailField(_('Email Address'), unique=True, null=False, blank=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Account(models.Model):
    user = models.OneToOneField(User, related_name='accounts', on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic', default='avatars/avatar.jpg', blank=True)
    profile_pic_thumbnail = ImageSpecField(source='profile_pic',
                                           processors=[ResizeToFill(80, 80)],
                                           format="JPEG",
                                           options={'quality': 60})
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, choices=Genders, null=True)
    address = models.TextField(max_length=255, blank=True, null=True, help_text="Home address")
    country = CountryField(blank_label='(select country)', blank=True, null=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.first_name is None and self.last_name is None:
            self.full_name = ""
        else:
            full_name = str(self.first_name) + " " + str(self.last_name)
            self.full_name = full_name
        super().save(*args, **kwargs)


class Author(models.Model):
    user = models.OneToOneField(Account, related_name="author", on_delete=models.CASCADE)
    about = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
