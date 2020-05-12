#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
from comment.forms import CommentForm


register = template.Library()


@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()


@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)

    initial_data = dict()
    initial_data['content_type'] = content_type.model
    initial_data['object_id'] = obj.pk
    initial_data['reply_comment_id'] = 0

    return CommentForm(initial=initial_data)


@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None).order_by('-comment_time')
