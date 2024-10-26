# -*- coding: utf-8 -*-
import os
from jinja2 import Template
from odoo import http


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
