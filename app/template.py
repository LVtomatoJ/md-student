import os
import logging
from setting import global_config
from typing import List, Dict
logger = logging.getLogger(__name__)


class TemplateManager:

    template_list: List[str] = []

    def load_template_list(self):
        for dir_name in os.listdir(global_config.file_path.template_dir):
            dir_path = os.path.join(global_config.file_path.template_dir, dir_name)
            if os.path.isdir(dir_path):
                self.template_list.append(dir_name)

    def __init__(self):
        self.load_template_list()

    def get_template_list(self) -> List[str]:
        return self.template_list

    def get_template_info(self, template_name: str) -> Dict[str, str]:
        index_template_path = os.path.join(global_config.file_path.template_dir, template_name, 'index.html')
        post_template_path = os.path.join(global_config.file_path.template_dir, template_name, 'post.html')
        with open(index_template_path, 'r') as f:
            index_template = f.read()
        with open(post_template_path, 'r') as f:
            post_template = f.read()
        return {
            'index_template': index_template,
            'post_template': post_template,
        }


if __name__ == '__main__':
    manager = TemplateManager()
    print(manager.get_template_list())
