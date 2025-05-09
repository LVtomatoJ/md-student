import toga
import os
import random
from pathlib import PosixPath
from toga.style.pack import COLUMN, Pack
from app.template import TemplateManager
from app.post import PostManager
from setting import global_config
from app.agent import Agent, AgentAsync
from jinja2 import Template
from model.post import PostRawFront, PostRaw
from app.control import Control
from datetime import datetime

agent = Agent()
async_agent = AgentAsync()
template_manager = TemplateManager()
post_manager = PostManager()
control = Control()


class GenderTemplateShowBox(toga.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = COLUMN
        self.flex = 1
        self.progress = toga.ProgressBar(max=100, value=0)
        self.add(self.progress)
        self.split_box = toga.SplitContainer(style=Pack(flex=1))
        self.index_page_web_view = toga.WebView(style=Pack(flex=1))
        self.post_page_web_view = toga.WebView(style=Pack(flex=1))
        self.split_box.content = [self.index_page_web_view, self.post_page_web_view]
        self.add(self.split_box)

    def update_progress(self, value):
        self.progress.value = value

    def update_web_view(self, index, content):
        if index == 0:
            self.index_page_web_view.set_content('https://127.0.0.1/index.html', content)
        elif index == 1:
            self.post_page_web_view.set_content('https://127.0.0.1/post.html', content)


class GenderTemplateWindow(toga.Box):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_template = None
        self.post_template = None
        self.direction = COLUMN
        self.main_window = main_window
        self.flex = 1
        self.prompt_text = toga.MultilineTextInput(placeholder="请输入模板风格生成提示", style=Pack(height=200))
        self.gender_button = toga.Button("生成")
        self.show_box = GenderTemplateShowBox(style=Pack(flex=1))
        self.save_button = toga.Button("保存")
        self.add(self.prompt_text)
        self.add(self.gender_button)
        self.add(self.show_box)
        self.add(self.save_button)
        self.gender_button.on_press = self.on_gender_button_click
        self.save_button.on_press = self.on_save_button_click

    async def on_gender_button_click(self, widget):
        await self.async_generate_index_page()
        await self.async_generate_post_page()

    async def on_save_button_click(self, widget):
        if self.index_template is None and self.post_template is None:
            await self.main_window.dialog(toga.InfoDialog('提示', '请先生成模版'))
            return
        initial_directory = os.path.join(os.getcwd(), global_config.file_path.template_dir)
        select_folder_dialog = toga.SelectFolderDialog("请选择模版保存路径", initial_directory=initial_directory)
        save_path = await self.main_window.dialog(select_folder_dialog)
        if save_path is not None:
            with open(os.path.join(save_path, 'index.html'), 'w') as f:
                f.write(self.index_template)
            with open(os.path.join(save_path, 'post.html'), 'w') as f:
                f.write(self.post_template)
            await self.main_window.dialog(toga.InfoDialog('提示', '模版保存成功'))

    async def async_generate_index_page(self):
        index_template = await self.generate_index_page()
        self.index_template = index_template
        index_template = Template(index_template)
        print(f'index_template: {index_template}')
        index_html = index_template.render(global_config.default_template_data.index_page_data)
        self.show_box.update_web_view(0, index_html)
        self.show_box.update_progress(40)

    async def async_generate_post_page(self):
        post_template = await self.generate_post_page()
        self.post_template = post_template
        post_template = Template(post_template)
        post_html = post_template.render(global_config.default_template_data.post_page_data)
        self.show_box.update_web_view(1, post_html)
        self.show_box.update_progress(80)

    def combine_prompt(self, base_prompt: str):
        prompt = base_prompt + "\n" + self.prompt_text.value + "\n" \
            + "请只返回HTML模板代码，使用Jinja2语法，不要包含其他说明文字。代码中应包含所有必要的CSS和JavaScript代码。"
        return prompt

    async def generate_index_page(self):
        async_agent = await AgentAsync.create()
        prompt = self.combine_prompt(global_config.default_prompt.index_page_prompt)
        template = await async_agent.generate_html_template(prompt)
        return template

    async def generate_post_page(self):
        async_agent = await AgentAsync.create()
        prompt = self.combine_prompt(global_config.default_prompt.post_page_prompt)
        template = await async_agent.generate_html_template(prompt)
        return template


class TemplateManagerWindow(toga.Box):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.direction = COLUMN
        self.flex = 1
        self.template_list = template_manager.get_template_list()
        self.template_selection = toga.Selection(items=self.template_list)
        self.show_box = GenderTemplateShowBox(style=Pack(flex=1))
        self.add(self.template_selection)
        self.add(self.show_box)
        self.template_selection.on_change = self.on_template_selection_change
        if len(self.template_list) > 0:
            self.template_selection.value = self.template_list[0]

    async def on_template_selection_change(self, widget):
        template_name = self.template_selection.value
        template_info = template_manager.get_template_info(template_name)
        index_template = template_info['index_template']
        post_template = template_info['post_template']
        index_html = Template(index_template).render(global_config.default_template_data.index_page_data)
        post_html = Template(post_template).render(global_config.default_template_data.post_page_data)
        self.show_box.update_web_view(0, index_html)
        self.show_box.update_web_view(1, post_html)


class ListItemButton(toga.Button):
    def __init__(self, post, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = post
        self.text = post.front.title
        self.file_name = post.file_name


class PostListBox(toga.Box):
    def __init__(self, post_list, on_post_button_click, on_create_button_click, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = COLUMN
        self.flex = 1
        self.create_button = toga.Button('创建')
        self.add(self.create_button)
        self.create_button.on_press = on_create_button_click
        self.post_list = post_list
        for post in self.post_list:
            post_button = ListItemButton(post)
            post_button.on_press = on_post_button_click
            self.add(post_button)


class PostInfoBox(toga.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = COLUMN
        self.flex = 1
        self.title = toga.TextInput(placeholder='标题')
        self.add(self.title)
        self.create_time = toga.TextInput(placeholder='创建时间')
        self.add(self.create_time)
        self.update_time = toga.TextInput(placeholder='更新时间')
        self.add(self.update_time)
        self.tags = toga.TextInput(placeholder='标签')
        self.add(self.tags)
        self.content = toga.MultilineTextInput(placeholder='内容', style=Pack(flex=1))
        self.add(self.content)
        self.save_button = toga.Button('保存')
        self.add(self.save_button)
        self.save_button.on_press = self.on_save_button_click

    def update_post_info(self, post, content):
        self.title.value = post.front.title
        self.content.value = content
        self.create_time.value = post.front.create_time
        self.update_time.value = post.front.update_time
        self.tags.value = post.front.tags
        self.file_name = post.file_name

    def on_save_button_click(self, widget):
        front = PostRawFront(
            title=self.title.value,
            create_time=self.create_time.value,
            update_time=self.update_time.value,
            tags=self.tags.value,
        )
        post_manager.save_post_md(front.model_dump(), self.content.value, self.file_name)


class PostManagerWindow(toga.Box):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.direction = COLUMN
        self.flex = 1
        self.post_list = post_manager.get_post_list()
        self.split_box = toga.SplitContainer(style=Pack(flex=1))
        self.post_list_box = PostListBox(self.post_list, self.on_post_button_click, self.on_create_button_click)
        self.post_info_box = PostInfoBox()
        self.split_box.content = [self.post_list_box, self.post_info_box]
        self.add(self.split_box)

    def on_post_button_click(self, widget):
        content = post_manager.get_post_content(widget.file_name)
        self.post_info_box.update_post_info(widget.post, content)

    async def on_create_button_click(self, widget):
        initial_directory = os.path.join(os.getcwd(), global_config.file_path.post_dir, f'{random.randint(1, 1000000)}.md') # noqa
        file_path: PosixPath = await self.main_window.dialog(toga.SaveFileDialog('请输入文件名',
                                                             suggested_filename=initial_directory))
        if file_path is not None:
            file_name = file_path.name
            post = PostRaw(file_name=file_name,
                           front=PostRawFront(title='',
                                              create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                              update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                              tags=''))
            self.post_info_box.update_post_info(post, '')

    def save_post_info_dialog(self, widget):
        self.main_window.dialog(toga.InfoDialog('提示', '保存成功'))


class ControlBox(toga.Box):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = COLUMN
        self.flex = 1
        self.main_window = main_window
        self.add(toga.Label('控制台'))
        self.template_selection = toga.Selection(items=template_manager.get_template_list())
        self.add(self.template_selection)
        self.render_all_page_button = toga.Button('渲染所有页面')
        self.add(self.render_all_page_button)
        self.render_all_page_button.on_press = self.on_render_all_page_button_click

    async def on_render_all_page_button_click(self, widget):
        control.render_all_page(self.template_selection.value)
        await self.main_window.dialog(toga.InfoDialog('提示', '渲染成功'))


class MyApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow()
        self.page_selection = toga.Selection(items=["模板生成", "模版管理", "文章管理", "控制台"])
        self.page_selection.on_change = self.on_page_selection_change
        self.content_box = toga.Box(style=Pack(flex=1))
        main_box = toga.Box(style=Pack(flex=1))
        main_box.add(self.page_selection)
        main_box.add(self.content_box)
        main_box.direction = COLUMN

        self.gender_template_window = GenderTemplateWindow(main_window=self.main_window)
        self.template_manager_window = TemplateManagerWindow(main_window=self.main_window)
        self.post_manager_window = PostManagerWindow(main_window=self.main_window)
        self.control_box = ControlBox(main_window=self.main_window)
        self.main_window.content = main_box
        self.main_window.show()
        self.page_selection.value = "模板生成"

    def on_page_selection_change(self, widget):
        main_box = toga.Box(style=Pack(flex=1))
        main_box.direction = COLUMN
        main_box.add(self.page_selection)
        if widget.value == "模板生成":
            main_box.add(self.gender_template_window)
        elif widget.value == "模版管理":
            main_box.add(self.template_manager_window)
        elif widget.value == "文章管理":
            main_box.add(self.post_manager_window)
        elif widget.value == "控制台":
            main_box.add(self.control_box)
        self.main_window.content = main_box


if __name__ == '__main__':
    app = MyApp("MD-student", "com.lvtomatoj.md-student")
    app.main_loop()
