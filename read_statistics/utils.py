#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail


def read_statistics_once_read(request, obj, pk):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read' % (ct.model, pk)
    if not request.COOKIES.get(key):
        readnum, _ = ReadNum.objects.get_or_create(content_type=ct, object_id=pk)
        readnum.read_num += 1
        readnum.save()

        date = timezone.now().date()
        readDetail, _ = ReadDetail.objects.get_or_create(content_type=ct, object_id=pk, date=date)
        readDetail.read_num += 1
        readDetail.save()

    return key


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7, 0, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime("%m/%d"))
        readDetails = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = readDetails.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)

    return dates, read_nums


def get_today_hot_data(content_type):
    date = timezone.now().date()
    readDetails = ReadDetail.objects.filter(content_type=content_type, date=date).order_by('-read_num')
    return readDetails[:7]


def get_yesterday_hot_data(content_type):
    date = timezone.now().date() - timedelta(days=1)
    readDetails = ReadDetail.objects.filter(content_type=content_type, date=date).order_by('-read_num')
    return readDetails[:7]


def get_seven_days_hot_data(content_type):
    today = timezone.now().date()
    before_seven_days_date = today - timedelta(days=7)
    readDetails = ReadDetail.objects.filter(content_type=content_type, date__lt=today, date__gte=before_seven_days_date)
    read_details_dict = {}
    for read_detail in readDetails:
        if read_detail.object_id not in read_details_dict:
            read_details_dict[read_detail.object_id] = read_detail
        else:
            read_details_dict[read_detail.object_id].read_num += read_detail.read_num

    read_details = [read_details_dict[key] for key in
                    sorted(read_details_dict, key=lambda x: read_details_dict[x].read_num, reverse=True)]

    return read_details[:10]


