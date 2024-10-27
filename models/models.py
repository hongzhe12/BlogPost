# -*- coding: utf-8 -*-

import pyperclip

from odoo import models, fields, api


class BlogPost(models.Model):
    _name = 'blog.post'  # 模型名称
    _description = 'Blog Post'  # 模型描述
    _rec_name = 'title'  # 用于在列表视图中显示记录的名称

    title = fields.Char(string='标题', required=True)  # 博客标题
    content_block_ids = fields.One2many('blog.content.block', 'post_id', string='内容块')  # 内容块
    summary = fields.Text(string='摘要')  # 博客摘要
    author_id = fields.Many2one('res.users', string='作者')  # 作者
    date_published = fields.Datetime(string='发布日期', default=fields.Datetime.now)  # 发布时间
    # media_video_ids = fields.Many2many(
    #     'media.video',
    #     'blog_post_media_video_rel',
    #     'blog_post_id',
    #     'media_video_id',
    #     string='视频')

    # @api.depends('content')
    # def _compute_summary(self):
    #     for record in self:
    #         print(record.content)
    #         soup = BeautifulSoup(record.content, 'html.parser')
    #         text = soup.get_text().strip().replace('\n', ' ')
    #         if len(record.content) > 15:
    #             record.summary = text[:15] + '...'
    #         else:
    #             record.summary = text[:15] + '...'


class ContentBlock(models.Model):
    _name = 'blog.content.block'
    _description = 'Content Block'
    name = fields.Char(string='块名称', required=True)
    post_id = fields.Many2one('blog.post', string='博客文章', ondelete='cascade')
    type = fields.Selection([
        ('text', '文本'),
        ('image', '图片'),
        ('video', '视频'),
        ('html', '超文本'),
    ], string='块类型', required=True)
    text_content = fields.Text('文本内容')  # 文本内容
    content = fields.Html(string='内容', required=True)  # Html内容
    image_content = fields.Binary('图片内容')  # 图片内容
    video_id = fields.Many2one('media.video', string='视频')  # 关联视频


class MediaVideo(models.Model):
    _name = 'media.video'
    _description = '视频'
    name = fields.Char(string='名称')
    video = fields.Binary(string='视频', attachment=True)
    url = fields.Char(string='视频地址', compute='_compute_url')

    # blog_post_ids = fields.Many2many(
    #     'blog.post',
    #     'blog_post_media_video_rel',
    #     'media_video_id',
    #     'blog_post_id',
    #     string='博客列表'
    # )

    @api.depends('video')
    def _compute_url(self):
        '''
        '/<model_name>/<int:record_id>/media/<string:field_name>'
        '''
        for record in self:
            record.url = f'/{record._name}/{record.id}/media/video'

    def copy_url(self):
        # 获取当前域名(带http协议头)
        domain = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        str_list = []
        for record in self:
            url = f'{domain}/{record._name}/{record.id}/media/video'
            str_list.append(url)

        pyperclip.copy("\n".join(str_list))
        self.env.user.notify_success("复制成功！")
