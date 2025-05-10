from setting import global_config
from app.template import TemplateManager
from app.post import PostManager
from collections import Counter
from jinja2 import Template
import os
import random

template_manager = TemplateManager()
post_manager = PostManager()


class Control:

    def __init__(self):
        pass

    def render_all_page(self, template_name: str = 'random'):
        if not os.path.exists(global_config.file_path.output_dir):
            os.makedirs(global_config.file_path.output_dir)
        if template_name == 'random':
            template_name = random.choice(template_manager.get_template_list())
        template_info = template_manager.get_template_info(template_name)
        index_template = template_info['index_template']
        post_template = template_info['post_template']
        tag_list_counter = Counter()
        post_list = post_manager.get_post_list()
        for post in post_list:
            post_content = post_manager.get_post_content(post.file_name)
            post_html = post_manager.post_md_to_html(post_content)
            post_toc = post_manager.post_html_to_toc(post_html)
            post_data = {
                'post': {
                    'title': post.front.title,
                    'create_time': post.front.create_time,
                    'update_time': post.front.update_time,
                    'tags': post.front.tags.split(','),
                    'content': post_html,
                },
                'toc': post_toc,
            }
            final_html = Template(post_template).render(post_data)
            output_path = os.path.join(global_config.file_path.output_dir, f'{post.file_name.split(".")[0]}.html')
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_path, 'w') as f:
                f.write(final_html)
            tag_list_counter.update(post.front.tags.split(','))
        index_data = {
            'blog_name': global_config.blog_name,
            'tags': [
                {
                    'tag_name': tag,
                    'tag_length': tag_list_counter[tag],
                }
                for tag in tag_list_counter
            ],
            'posts': [
                {
                    'post_id': post.file_name,
                    'title': post.front.title,
                    'create_time': post.front.create_time,
                    'update_time': post.front.update_time,
                    'tags': post.front.tags.split(','),
                    'url': f'/{post.file_name.split(".")[0]}.html',
                } for post in post_list
            ]
        }
        index_html = Template(index_template).render(index_data)
        with open(os.path.join(global_config.file_path.output_dir, 'index.html'), 'w') as f:
            f.write(index_html)
