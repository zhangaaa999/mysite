from threading import Thread
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class SendEmail(Thread):
    def __init__(self, subject, html_message, email, fail_silently=False):
        Thread.__init__(self)
        self.subject = subject
        self.html_message = html_message
        self.email = email
        self.fail_silently = fail_silently

    def run(self):
        send_mail(subject=self.subject,
                  message='',
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[self.email],
                  fail_silently=False,
                  html_message=self.html_message)


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.DO_NOTHING)

    parent = models.ForeignKey('self', related_name='replied_comments', null=True, on_delete=models.DO_NOTHING)
    root = models.ForeignKey('self', related_name='root_comments', null=True, on_delete=models.DO_NOTHING)
    reply_to = models.ForeignKey(User, related_name='replied_users', null=True, on_delete=models.DO_NOTHING)

    def send_email(self):
        if hasattr(self.content_object, 'get_email'):
            email = self.content_object.get_email()
            if email:
                subject = "评论邮件通知"
                context = dict()
                context['comment_text'] = "您有一条评论信息: \n%s" % self.text
                context['url'] = self.content_object.get_url()
                html_message = render_to_string('comment/send_email.html', context)
                send_email = SendEmail(subject, html_message, email)
                send_email.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']
