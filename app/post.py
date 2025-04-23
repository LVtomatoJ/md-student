import yaml
import os
from setting import global_config
from typing import List
from model.post import PostRaw, PostTemplateTocItemH2, PostTemplateTocItem, PostRawFront
from markdown import markdown
from lxml import html


class PostManager:

    post_list: List[PostRaw] = []

    def __init__(self):
        self.init_post_list()

    def split_post_file(self, post_content: str):
        split_content = post_content.split('---', 2)
        front = split_content[1]
        front_dict = yaml.safe_load(front)
        content = split_content[2]
        return front_dict, content

    def read_post_file(self, file_path: str):
        with open(file_path, 'r') as f:
            post_content = f.read()
            front_dict, _ = self.split_post_file(post_content)
            return PostRaw(front=front_dict)

    def init_post_list(self):
        post_dir = os.path.join(global_config.file_path.post_dir)
        post_files = os.listdir(post_dir)
        post_list = []
        for post_file in post_files:
            file_path = os.path.join(post_dir, post_file)
            post = self.read_post_file(file_path)
            post.file_name = post_file
            post_list.append(post)
        self.post_list = post_list

    def get_post_list(self) -> List[PostRaw]:
        return self.post_list

    def get_post_content(self, file_name: str) -> str:
        post_dir = os.path.join(global_config.file_path.post_dir)
        file_path = os.path.join(post_dir, file_name)
        with open(file_path, 'r') as f:
            post_content = f.read()
            _, content = self.split_post_file(post_content)
            return content

    def post_md_to_html(self, post_content: str) -> str:
        return markdown(post_content, extensions=['toc'])

    def post_html_to_toc(self, post_html: str) -> List[PostTemplateTocItem]:
        tree = html.fromstring(post_html)
        h1_list = tree.findall('.//h1')
        toc = []
        for i, h1 in enumerate(h1_list):
            toc_item = PostTemplateTocItem(
                title=h1.text_content(),
                id=h1.attrib['id'],
                h2s=[]
            )
            next_h1 = h1_list[i + 1] if i + 1 < len(h1_list) else None
            current = h1.getnext()
            while current is not None and (next_h1 is None or current != next_h1):
                if current.tag == 'h2':
                    toc_item.h2s.append(PostTemplateTocItemH2(
                        title=current.text_content(),
                        id=current.attrib['id']
                    ))
                current = current.getnext()
            toc.append(toc_item)
        return toc

    def save_post_md(self, front: PostRawFront, post_content: str, file_name: str):
        post_dir = os.path.join(global_config.file_path.post_dir)
        file_path = os.path.join(post_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(f'---\n{yaml.dump(front)}\n---\n{post_content}')


if __name__ == '__main__':

    def main():
        post_manager = PostManager()
        post_content = post_manager.get_post_content('SecondPost.md')
        post_html = post_manager.post_md_to_html(post_content)
        toc = post_manager.post_html_to_toc(post_html)
        print(toc)

    main()
