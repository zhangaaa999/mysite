#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType
from likes.models import LikeCount, LikeRecord


register = template.Library()


@register.simple_tag
def get_like_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
    return like_count.liked_num


@register.simple_tag
def is_active(obj, user):
    if user.is_authenticated:
        content_type = ContentType.objects.get_for_model(obj)
        if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=user).exists():
            return "active"

    return ""
