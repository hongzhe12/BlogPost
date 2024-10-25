# -*- coding: utf-8 -*-

from odoo import models, fields

class BlogPost(models.Model):
    _name = 'blog.post'  # 模型名称
    _description = 'Blog Post'  # 模型描述

    title = fields.Char(string='标题', required=True)  # 博客标题
    content = fields.Text(string='内容', required=True)  # 博客内容
    summary = fields.Text(string='摘要')  # 博客摘要
    author_id = fields.Many2one('res.users', string='作者')  # 作者
    date_published = fields.Datetime(string='发布日期', default=fields.Datetime.now)  # 发布时间
    image = fields.Binary(string='图片')  # 博客图片




