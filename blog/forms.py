# -*- coding: utf-8 -*-
from django import forms
# from tinymce.widgets import TinyMCE
from mptt.forms import TreeNodeChoiceField
from .models import Comment, Post


# class PostForm(forms.ModelForm):
#     # content = forms.CharField(
#     #     widget=TinyMCE(attrs={"cols": 80, "rows": 15, "class": "form-control"})
#     # )
#
#     class Meta:
#         model = Post
#         fields = ("title", "overview", "content", "featured", "category", "thumbnail")


# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ("content",)


class NewCommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update(
            {'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comment
        fields = ('parent', 'content',)

        widgets = {

            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super(NewCommentForm, self).save(*args, **kwargs)
