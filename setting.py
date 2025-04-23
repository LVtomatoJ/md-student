from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime


class filePaths(BaseSettings):
    post_dir: str = "posts"
    template_dir: str = "templates"
    output_dir: str = "output"


class defaultPrompt(BaseSettings):
    index_page_prompt: str = """
请生成一个博客首页的HTML模板代码，使用Jinja2模板语法，要求如下：
需要插入的数据结构(模版中应只包含以下数据结构，不要包含其他数据结构)：
- 博客名称：{{ blog_name }}
- 标签列表：{% for tag in tags %}
  - tag_name: {{ tag.tag_name }}
  - tag_length: {{ tag.tag_length }}
{% endfor %}
- 文章列表：{% for post in posts %}
  - post_id: {{ post.post_id }}
  - title: {{ post.title }}
  - create_time(yyyy-mm-dd hh:mm:ss): {{ post.create_time }}
  - tags: {{ post.tags }}
  - url: {{ post.url }}
{% endfor %}。
标签应实现筛选功能
以下为风格要求：
"""
    post_page_prompt: str = """
请生成一个博客文章页面的HTML模板代码，使用Jinja2模板语法，要求如下：

需要插入的数据结构(模版中应只包含以下数据结构，不要包含其他数据结构)：
- 文章基本信息：
  * post_id: {{ post.post_id }}
  * title: {{ post.title }}
  * tags: {{ post.tags }}
  * create_time(yyyy-mm-dd hh:mm:ss): {{ post.create_time }}
  * update_time(yyyy-mm-dd hh:mm:ss): {{ post.update_time }}
  * content: {{ post.content|safe }}  # 文章内容（HTML格式）
- 目录结构：
  * 主标题列表：{% for h1 in toc %}
    - title: {{ h1.title }}
    - id: {{ h1.id }}
    - h2列表：
      {% for h2 in h1.h2s %}
      - title: {{ h2.title }}
      - id: {{ h2.id }}
      {% endfor %}
  {% endfor %}
以下为风格要求：
"""


class defaultTemplateData(BaseSettings):
    index_page_data: dict = {
        "blog_name": "MD-student",
        "tags": [
            {"tag_name": "测试", "tag_length": 2},
            {"tag_name": "python", "tag_length": 2},
            {"tag_name": "AI", "tag_length": 2},
        ],
        "posts": [
            {
                "post_id": 1,
                "title": "Python测试学习！",
                "create_time": datetime.strptime("2024-03-20 12:01:03", "%Y-%m-%d %H:%M:%S"),
                "tags": ["测试", "python"],
                "url": "/posts/python-test.html"
            },
            {
                "post_id": 2,
                "title": "AI如何进行测试？",
                "create_time": datetime.strptime("2024-03-21 12:24:02", "%Y-%m-%d %H:%M:%S"),
                "tags": ["测试", "AI"],
                "url": "/posts/ai-test.html"
            },
            {
                "post_id": 3,
                "title": "用python实现一个agent",
                "create_time": datetime.strptime("2024-03-22 12:24:02", "%Y-%m-%d %H:%M:%S"),
                "tags": ["python", "AI"],
                "url": "/posts/python-agent.html"
            }
        ]
    }
    post_page_data: dict = {
        "post": {
            "post_id": 1,
            "title": "Python测试学习！",
            "tags": ["测试", "python"],
            "create_time": datetime.strptime("2024-03-20 12:01:03", "%Y-%m-%d %H:%M:%S"),
            "update_time": datetime.strptime("2024-03-21 12:24:02", "%Y-%m-%d %H:%M:%S"),
            "content": """
        <h1 id="content-chapter-1">第一章：Python基础</h1>
        <h2 id="content-python-intro">1.1 Python简介</h2>
        <p>Python是一种高级编程语言，以其简洁的语法和丰富的库而闻名。它的设计哲学强调代码的可读性，其语法允许程序员用更少的代码行表达概念。</p>
        <pre><code class="language-python">print("Hello, World!")</code></pre>

        <h2 id="content-dev-env">1.2 开发环境搭建</h2>
        <p>搭建Python开发环境是学习的第一步。我们需要安装Python解释器、包管理工具pip，以及一个合适的IDE。</p>

        <h2 id="content-basic-syntax">1.3 基础语法</h2>
        <p>Python的基础语法包括变量、数据类型、控制流、函数等概念。这些是编程的基础，需要熟练掌握。</p>

        <h1 id="content-chapter-2">第二章：测试基础</h1>
        <h2 id="content-test-concept">2.1 测试概念</h2>
        <p>测试是软件开发中不可或缺的环节。它帮助我们确保代码的质量和可靠性。</p>

        <h2 id="content-test-methods">2.2 测试方法</h2>
        <p>常见的测试方法包括单元测试、集成测试、系统测试等。每种测试方法都有其特定的用途和优势。</p>

        <h2 id="content-test-framework">2.3 测试框架</h2>
        <p>Python中有多个优秀的测试框架，如pytest、unittest等。选择合适的框架可以提高测试效率。</p>

        <h1 id="content-chapter-3">第三章：自动化测试</h1>
        <h2 id="content-auto-test-intro">3.1 自动化测试概述</h2>
        <p>自动化测试是现代软件开发中的重要组成部分，它可以提高测试效率，减少人为错误。</p>

        <h2 id="content-auto-test-tools">3.2 自动化测试工具</h2>
        <p>介绍常用的自动化测试工具，如Selenium、PyAutoGUI等，以及它们的使用场景。</p>

        <h2 id="content-auto-test-practice">3.3 自动化测试实践</h2>
        <p>通过实际案例，展示如何设计和实现自动化测试用例。</p>

        <h1 id="content-chapter-4">第四章：性能测试</h1>
        <h2 id="content-perf-test-intro">4.1 性能测试概述</h2>
        <p>性能测试关注系统的响应时间、并发处理能力、资源使用等指标。</p>

        <h2 id="content-perf-test-tools">4.2 性能测试工具</h2>
        <p>介绍常用的性能测试工具，如Locust、JMeter等，以及它们的特点和适用场景。</p>

        <h2 id="content-perf-test-metrics">4.3 性能测试指标</h2>
        <p>详细说明性能测试中需要关注的各项指标，如响应时间、吞吐量、并发用户数等。</p>

        <h1 id="content-chapter-5">第五章：测试最佳实践</h1>
        <h2 id="content-test-strategy">5.1 测试策略</h2>
        <p>制定合理的测试策略，包括测试范围、测试优先级、测试资源分配等。</p>

        <h2 id="content-test-maintenance">5.2 测试维护</h2>
        <p>如何维护测试用例，确保测试代码的质量和可维护性。</p>

        <h2 id="content-test-ci-cd">5.3 测试与CI/CD</h2>
        <p>将测试集成到持续集成和持续部署流程中，实现自动化测试和部署。</p>
        """
        },
        "toc": [
            {
                "title": "第一章：Python基础",
                "id": "content-chapter-1",
                "h2s": [
                    {
                        "title": "1.1 Python简介",
                        "id": "content-python-intro"
                    },
                    {
                        "title": "1.2 开发环境搭建",
                        "id": "content-dev-env"
                    },
                    {
                        "title": "1.3 基础语法",
                        "id": "content-basic-syntax"
                    }
                ]
            },
            {
                "title": "第二章：测试基础",
                "id": "content-chapter-2",
                "h2s": [
                    {
                        "title": "2.1 测试概念",
                        "id": "content-test-concept"
                    },
                    {
                        "title": "2.2 测试方法",
                        "id": "content-test-methods"
                    },
                    {
                        "title": "2.3 测试框架",
                        "id": "content-test-framework"
                    }
                ]
            },
            {
                "title": "第三章：自动化测试",
                "id": "content-chapter-3",
                "h2s": [
                    {
                        "title": "3.1 自动化测试概述",
                        "id": "content-auto-test-intro"
                    },
                    {
                        "title": "3.2 自动化测试工具",
                        "id": "content-auto-test-tools"
                    },
                    {
                        "title": "3.3 自动化测试实践",
                        "id": "content-auto-test-practice"
                    }
                ]
            },
            {
                "title": "第四章：性能测试",
                "id": "content-chapter-4",
                "h2s": [
                    {
                        "title": "4.1 性能测试概述",
                        "id": "content-perf-test-intro"
                    },
                    {
                        "title": "4.2 性能测试工具",
                        "id": "content-perf-test-tools"
                    },
                    {
                        "title": "4.3 性能测试指标",
                        "id": "content-perf-test-metrics"
                    }
                ]
            },
            {
                "title": "第五章：测试最佳实践",
                "id": "content-chapter-5",
                "h2s": [
                    {
                        "title": "5.1 测试策略",
                        "id": "content-test-strategy"
                    },
                    {
                        "title": "5.2 测试维护",
                        "id": "content-test-maintenance"
                    },
                    {
                        "title": "5.3 测试与CI/CD",
                        "id": "content-test-ci-cd"
                    }
                ]
            }
        ]
    }


class Settings(BaseSettings):
    file_path: filePaths = filePaths()
    api_key: str
    default_prompt: defaultPrompt = defaultPrompt()
    default_template_data: defaultTemplateData = defaultTemplateData()
    model_config = SettingsConfigDict(env_file=".env")
    blog_name: str = "MD-student"


global_config = Settings()
