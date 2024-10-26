# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs4 import BeautifulSoup

from odoo.tools.populate import compute


class BlogPost(models.Model):
    _name = 'blog.post'  # 模型名称
    _description = 'Blog Post'  # 模型描述

    title = fields.Char(string='标题', required=True)  # 博客标题
    content = fields.Html(string='内容', required=True)  # 博客内容
    summary = fields.Text(string='摘要', compute="_compute_summary")  # 博客摘要
    author_id = fields.Many2one('res.users', string='作者')  # 作者
    date_published = fields.Datetime(string='发布日期', default=fields.Datetime.now)  # 发布时间
    video_url = fields.Char(string='视频地址')  # 视频地址

    @api.depends('content')
    def _compute_summary(self):
        for record in self:
            soup = BeautifulSoup(record.content, 'html.parser')
            text = soup.get_text().strip().replace('\n', ' ')
            if len(record.content) > 15:
                record.summary = text[:15] + '...'
            else:
                record.summary = text[:15] + '...'


class MediaVideo(models.Model):
    _name = 'media.video'
    _description = '视频'
    name = fields.Char(string='名称')
    video = fields.Binary(string='视频', attachment=True)
    url = fields.Char(string='视频地址',compute = '_compute_url')

    @api.depends('video')
    def _compute_url(self):
        '''
        '/<model_name>/<int:record_id>/media/<string:field_name>'
        '''
        for record in self:
            record.url = f'/{record._name}/{record.id}/media/video'


