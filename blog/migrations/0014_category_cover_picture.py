# Generated by Django 3.1.8 on 2022-09-18 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20220901_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cover_picture',
            field=models.ImageField(blank=True, null=True, upload_to='category/thumbnail', verbose_name='Thumbnail'),
        ),
    ]
