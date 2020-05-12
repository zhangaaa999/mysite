#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Coeus
Date: 2020/1/15 17:37
Desc: 
"""

from datetime import timedelta
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache

from blog.models import Blog
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, \
    get_seven_days_hot_data


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[: 10]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    seven_days_hot_blogs = cache.get('seven_days_hot_blogs')
    if seven_days_hot_blogs is None:
        seven_days_hot_blogs = get_7_days_hot_blogs()
        cache.set('seven_days_hot_blogs', seven_days_hot_blogs, 3600)

    context = dict()
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_data'] = get_yesterday_hot_data(blog_content_type)
    # context['seven_days_data'] = get_seven_days_hot_data(blog_content_type)
    context['seven_days_blogs'] = get_7_days_hot_blogs
    return render(request, "home.html", context)
