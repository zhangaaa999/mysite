from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import LikeCount, LikeRecord


def error_response(code, message):
    data = dict()
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def success_response(liked_num, is_active):
    data = dict()
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    data['is_active'] = is_active
    return JsonResponse(data)


def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return error_response(400, '你没有登录')

    content_type_str = request.GET.get('content_type')
    content_type = ContentType.objects.get(model=content_type_str)
    object_id = request.GET.get('object_id')
    # is_like = request.GET.get('is_like')

    like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
    if created:
        # 未点赞过, 现在进行点赞, 对该博客的点赞数+1
        like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
        like_count.liked_num += 1
        like_count.save()
        is_active = True
    else:
        # 已经点赞过了, 现在要取消点赞, 点赞技术, 并对该博客的点赞数-1
        like_record.delete()
        like_count = LikeCount.objects.get(content_type=content_type, object_id=object_id)
        like_count.liked_num -= 1
        like_count.save()
        is_active = False

    return success_response(like_count.liked_num, is_active)
