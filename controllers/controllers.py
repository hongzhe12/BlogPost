# -*- coding: utf-8 -*-
import os

from jinja2 import Template

from odoo.http import request
from datetime import datetime, date
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

class BlogpostController(http.Controller):
    @http.route('/query_blogpost/<int:blogpost_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def query_blogpost(self, blogpost_id):
        blogpost = request.env['blog.post'].sudo().browse(blogpost_id)
        if not blogpost.exists():
            return Failure('数据不存在！')

        context = {}
        context.update(blogpost.read()[0])

        # 转换datetime字段
        for key, value in context.items():
            if isinstance(value, datetime):
                context[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # 转换为字符串格式

        if blogpost and hasattr(blogpost,'image'):
            del context['image']
            context['image_url'] = '/blogpost/image/%s' % blogpost_id  # Generate image URL

        return Success("获取成功！",data=context)

    @http.route('/upload_blogpost', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def upload_blogpost(self, **kwargs):
        values = {key: kwargs[key] for key in kwargs}

        # Check if 'image' is in the uploaded files
        if 'image' in request.httprequest.files:
            image_file = request.httprequest.files['image']
            image_data = image_file.read()
            # Encode the image to base64
            values['image'] = base64.b64encode(image_data)

        new_blogpost = request.env['blog.post'].sudo().create(values)
        return Success("上传成功！")

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

    @http.route('/<model_name>/<int:record_id>/media/<string:field_name>', type='http', auth='public', methods=['GET'],csrf=False)
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

    @http.route('/delete_blogpost/<int:blogpost_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def delete_blogpost(self, blogpost_id):
        blogpost = request.env['blog.post'].sudo().browse(blogpost_id)
        if not blogpost.exists():
            return Failure("数据不存在！")
        blogpost.sudo().unlink()
        return Success("删除成功！")


    @http.route('/list_blogpost_pages', type='http', auth='public', methods=['GET'], csrf=False)
    def list_blogpost_pages(self,**kw):
        # 获取页码和每页条目数量，默认为1和10
        page = int(kw.get('page', 1))
        per_page = int(kw.get('per_page', 10))

        offset = (page - 1) * per_page
        limit = per_page

        blogposts = request.env['blog.post'].sudo().search([], offset=offset, limit=limit) # # order='start_time DESC'
        context = []
        for blogpost in blogposts:
            item = {'image_url': ''}
            item.update(blogpost.read()[0])

            # 获取字典的键列表，避免遍历时修改字典导致的错误
            for key in list(item.keys()):
                value = item[key]

                # 删除二进制字段
                if isinstance(value, bytes):
                    del item[key]
                    # 生成图像 URL
                    item[key] = f'/{key}/image/%s' % blogpost.id  # 生成图像 URL

                # 删除关联字段（以 _id 或 _ids 结尾）
                elif key.endswith("_id") or key.endswith("_ids"):
                    del item[key]

                # 转换 datetime 字段为字符串格式
                elif isinstance(value, datetime):
                    item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, date):
                    item[key] = value.strftime("%Y-%m-%d")  # 处理 date 类型字段
            context.append(item)

        return Success("获取成功！", data=context)

    @http.route('/list_blogpost_pages', type='http', auth='public', methods=['GET'], csrf=False)
    # def list_blogpost_pages(self,**kw):
    #     # 获取页码和每页条目数量，默认为1和10
    #     page = int(kw.get('page', 1))
    #     per_page = int(kw.get('per_page', 10))
    #
    #     offset = (page - 1) * per_page
    #     limit = per_page
    #
    #     blogposts = request.env['blog.post'].sudo().search([], offset=offset, limit=limit) # # order='start_time DESC'
    #     context = []
    #     fields_to_return = ['id', 'dc', '自定义字段']
    #     for blogpost in blogposts:
    #         item = {}
    #         data = blogpost.read()[0]
    #         for field in fields_to_return:
    #             if field in data:
    #                 item[field] = data[field]
    #         for key, value in item.items():
    #             if isinstance(value, datetime):
    #                 item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    #             elif isinstance(value, date):
    #                 item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    #         if blogpost and hasattr(blogpost, 'image'):
    #             del item['image']
    #             item['image_url'] = '/blogpost/image/%s' % blogpost.id
    #         context.append(item)
    #     return Success("获取成功！", data=context)



    @http.route('/update_blogpost/<int:blogpost_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def update_blogpost(self, blogpost_id, **kwargs):
        blogpost = request.env['blog.post'].sudo().browse(blogpost_id)
        if not blogpost.exists():
            return Failure("数据不存在！")

        # 预处理参数
        values = {}
        for key, value in kwargs.items():
            if key in ['activity_state']:
                values[key] = value.lower() == 'true'  # 转换为布尔值
            elif isinstance(value, str) and value.lower() in ['true', 'false']:
                values[key] = value.lower() == 'true'  # 处理其他布尔字段
            elif isinstance(value, str) and 'T' in value:  # 检测 ISO 8601 格式
                try:
                    values[key] = datetime.fromisoformat(value)  # 转换为 datetime 对象
                except ValueError as e:
                    return Failure(f"无效的日期格式: {str(e)}")
            elif key == 'activity_ids' and not value:
                continue  # 跳过空列表
            else:
                values[key] = value

        # Check if 'image' is in the uploaded files
        if 'image' in request.httprequest.files:
            image_file = request.httprequest.files['image']
            image_data = image_file.read()
            # Encode the image to base64
            values['image'] = base64.b64encode(image_data)

        blogpost.sudo().write(values)

        # Update the image URL if necessary
        # image_url = '/blogpost/image/%s' % blogpost_id
        # blogpost.sudo().write({'image_url': image_url})

        return Success("更新成功！")

    @http.route('/get_blogpost_field/<int:blogpost_id>/<field_name>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_field_value(self, blogpost_id, field_name):
        blogpost = request.env['blog.post'].sudo().browse(blogpost_id)
        if not blogpost.exists():
            return Failure('数据不存在！')

        if not hasattr(blogpost, field_name):
            return Failure(f'字段 {field_name} 不存在！')

        field_value = getattr(blogpost, field_name)

        # 转换datetime字段
        if isinstance(field_value, datetime):
            field_value = field_value.isoformat()

        return Success("获取成功！", data={field_name: field_value})

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



