# -*- coding: utf-8 -*-
import os
from jinja2 import Template
from odoo.http import request
from datetime import date
import json
import base64
from odoo import http
from datetime import datetime


def Success(message="成功！", data=''):
    response_data = json.dumps({
        "status": 200,
        "message": message,
        "data": data
    })
    return http.Response(response_data, status=200, mimetype='application/json')


def Failure(message="失败！", data=''):
    response_data = json.dumps({
        "status": 400,
        "message": message,
        "data": data
    })
    return http.Response(response_data, status=400, mimetype='application/json')


class MediavideoController(http.Controller):

    @http.route('/<model_name>/<int:record_id>/images', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all_images(self, model_name, record_id, **kwargs):
        # 将模型名称中的点号替换为下划线
        model_name = model_name.replace('_', '.')

        # 获取记录
        record = request.env[model_name].sudo().browse(record_id)

        # 检查记录是否存在
        if not record:
            return request.not_found()

        # 查找所有二进制字段
        binary_fields = {field: field_def for field, field_def in record.fields_get().items() if
                         field_def['type'] == 'binary'}

        # 生成每个二进制字段的 URL
        media_urls = {}
        for field, field_def in binary_fields.items():
            media_urls[field] = f'/{model_name.replace(".", "_")}/{record_id}/media/{field}'

        return Success("媒体列表获取成功！", data=media_urls)

    @http.route('/<model_name>/<int:record_id>/media/<string:field_name>', type='http', auth='public', methods=['GET'],
                csrf=False)
    def get_media_field(self, model_name, record_id, field_name, **kwargs):
        # 将模型名称中的下划线替换为点号
        model_name = model_name.replace('_', '.')

        # 获取记录
        record = request.env[model_name].sudo().browse(record_id)

        # 检查记录是否存在和字段是否为二进制字段
        if not record or field_name not in record.fields_get() or record.fields_get()[field_name]['type'] != 'binary':
            return request.not_found()

        # 获取媒体数据
        media_data = getattr(record, field_name, None)
        if not media_data:
            return request.not_found()

        # 解码 Base64 数据
        try:
            media_data = base64.b64decode(media_data)
        except Exception as e:
            return request.not_found()  # 处理解码错误

        # 确定媒体类型并设置正确的 MIME 类型
        field_def = record.fields_get()[field_name]
        content_type = 'application/octet-stream'  # 默认类型
        if field_name == 'image':
            content_type = 'image/png'
        elif field_name == 'video':
            content_type = 'video/mp4'  # 假设视频格式为 mp4
        elif field_name == 'audio':
            content_type = 'audio/mpeg'  # 假设音频格式为 mp3

        # 返回媒体内容
        return request.make_response(media_data, headers=[('Content-Type', content_type)])


class BlogpostController(http.Controller):
    @http.route('/blog', auth='public', website=True)
    def blog_index(self):
        posts = http.request.env['blog.post'].search([])  # 获取所有博客文章

        # 读取 Jinja2 模板文件
        template_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'src', 'templates', 'blog_index.html')
        with open(template_path, encoding='utf-8') as f:
            jinja_template = f.read()

        template = Template(jinja_template)
        rendered_html = template.render(posts=posts)  # 渲染模板
        return rendered_html  # 返回渲染的 HTML

    @http.route('/blog/<model("blog.post"):post>', auth='public', website=True)
    def blog_post(self, post):
        # 读取 Jinja2 模板文件
        template_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'src', 'templates', 'blog_post.html')
        with open(template_path, encoding='utf-8') as f:
            jinja_template = f.read()

        template = Template(jinja_template)
        rendered_html = template.render(post=post)  # 渲染模板
        return rendered_html  # 返回渲染的 HTML
