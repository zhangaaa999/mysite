from markdown import markdown
from collections import OrderedDict
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read


def get_blog_list_common_data(request, blogs_all_list):
    # 设置分页相关
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number
    page_range = [num for num in range(current_page_num - 2, current_page_num + 3) if 0 < num < paginator.num_pages + 1]
    if current_page_num > 4:
        page_range.insert(0, '...')
    if current_page_num > 3:
        page_range.insert(0, 1)
    if current_page_num < paginator.num_pages - 3:
        page_range.append('...')
    if current_page_num < paginator.num_pages - 2:
        page_range.append(paginator.num_pages)

    blog_type_list = BlogType.objects.annotate(blog_count=Count('blog'))

    # 获取日期归档下对应的博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = OrderedDict()
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = dict()
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = blog_type_list
    context['blog_dates'] = blog_dates_dict
    return context


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request, "blog/blog_list.html", context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type

    return render(request, "blog/blogs_with_type.html", context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)

    return render(request, "blog/blogs_with_date.html", context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    blog.content = markdown(blog.content,
                            extensions=[
                                'markdown.extensions.extra',
                                'markdown.extensions.codehilite',
                                'markdown.extensions.toc',
                            ])

    read_cookie_key = read_statistics_once_read(request, blog, blog_pk)

    context = dict()
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()

    response = render(request, "blog/blog_detail.html", context)
    response.set_cookie(read_cookie_key, 'true')

    return response
