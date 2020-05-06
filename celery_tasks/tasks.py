# _*_ encoding:utf-8 _*_

from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext

from celery import Celery

import os

# 在任务处理者一端加这几句（django环境初始化）
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fresh.settings")
django.setup()

from goods.models import *

# 需要添加这几句，不然celery运行会报错
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 创建一个celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://192.168.0.107:6379/8')


# 任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""

    subject = '天天生鲜注册激活'
    message = ''
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/>' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' \
                   % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)


@app.task
def generate_static_index_html():
    """生成首页静态页面"""
    # 获取商品种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')  # 0 1 2 3

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息跟文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模版上下文
    context = {
        'types': types,
        'goods_banners': goods_banners,
        'promotion_banners': promotion_banners
    }

    # 使用模版
    # 1.加载模版文件，返回模版对象
    temp = loader.get_template('static_index.html')

    # 2.模版渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
