from django.shortcuts import render_to_response, get_object_or_404
from .models import Blog, BlogType, ReadNum
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count

each_page_blogs_number = 2

# 公共方法，供其他方法继承
def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOG_NUMBER) # 每10篇进行分页
    page_num = request.GET.get('page', 1) # 获取页面参数(get请求)
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number # 获取当前页码
    page_range = [i for i in range(current_page_num-2, current_page_num+3) if i > 0 and (i <= paginator.num_pages)]
    # 加上省略号
    if page_range[0] >= 3:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, 
                                        created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    # 统计每个分类中博客数量
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_range'] = page_range
    context['blog_dates'] = blog_dates_dict
    return context
 
# Create your views here.
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blog_list.html', context)

def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk )
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)

    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render_to_response('blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)

    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render_to_response('blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    context = {}
    blog = get_object_or_404(Blog, pk=blog_pk)
    # 根据cookie是否存在计数阅读量
    if not request.COOKIES.get('blog_%s_read' % blog_pk):
        if ReadNum.objects.filter(blog=blog).count():
            # 存在记录
            readnum = ReadNum.objects.get(blog=blog)
        else:
            # 不存在对应的记录
            readnum = ReadNum(blog=blog)
        # 技术加1
        readnum.read_num += 1
        readnum.save()

    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last() # 根据时间获取前一条博客
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response =  render_to_response('blog/blog_detail.html', context)
    response.set_cookie('blog_%s_read' % blog_pk, 'true') # 浏览器关闭cookie失效
    return response