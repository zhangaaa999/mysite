from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User


class LikeCount(models.Model):
    liked_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class LikeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_time = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')



# class ReadNumExpandMethod:
#     def read_num(self):
#         try:
#             ct = ContentType.objects.get_for_model(self)
#             readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
#             return readnum.read_num
#         except exceptions.ObjectDoesNotExist:
#             return 0
#
#
# class ReadDetail(models.Model):
#     date = models.DateField(default=timezone.now)
#     read_num = models.IntegerField(default=0)
#
#     content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
