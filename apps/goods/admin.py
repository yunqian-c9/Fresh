# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *

from django.contrib import admin
from django.core.cache import cache


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新数据时调用"""
        super(BaseModelAdmin, self).save_model(request, obj, form, change)

        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除数据时调用"""
        super(BaseModelAdmin, self).delete_model(request, obj)

        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页缓存数据
        cache.delete('index_page_data')


admin.site.register([GoodsSKU, Goods])


@admin.register(IndexGoodsBanner)
class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


@admin.register(GoodsType)
class GoodsTypeAdmin(BaseModelAdmin):
    pass


@admin.register(IndexPromotionBanner)
class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


@admin.register(IndexTypeGoodsBanner)
class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass
