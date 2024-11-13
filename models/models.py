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


class ContentBlock(models.Model):
    _name = 'blog.content.block'
    _description = 'Content Block'
    _order = 'sequence'

    sequence = fields.Integer(string='序号', required=True, default=lambda self: self._get_next_sequence())
    post_id = fields.Many2one('blog.post', string='博客文章', ondelete='cascade')
    type = fields.Selection([
        ('video', '视频'),
        ('html', '超文本'),
    ], string='块类型', required=True)

    content = fields.Html(string='内容')  # Html内容
    video_id = fields.Many2one('media.video', string='视频')  # 关联视频

    def _get_next_sequence(self):
        # 获取当前模型的最大sequence值 + 1
        last_sequence = self.env['blog.content.block'].search([], order='sequence desc', limit=1).sequence
        return last_sequence + 1 if last_sequence else 1


class MediaVideo(models.Model):
    _name = 'media.video'
    _description = '视频'
    name = fields.Char(string='名称')
    video = fields.Binary(string='视频', attachment=True)
    url = fields.Char(string='视频地址', compute='_compute_url')

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
