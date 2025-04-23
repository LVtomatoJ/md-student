from openai import AsyncOpenAI, OpenAI
from setting import global_config


class AgentAsync:

    client: AsyncOpenAI

    @classmethod
    async def create(cls) -> 'AgentAsync':
        instance = cls()
        instance.client = AsyncOpenAI(api_key=global_config.api_key, base_url="https://api.deepseek.com")
        return instance

    async def singel_chat(self, prompt: str):
        response = await self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        res = response.choices[0].message.content
        return res

    async def generate_html_template(self, prompt: str):
        res = await self.singel_chat(prompt)
        html_res = res.replace('```html', '').replace('```', '').strip()
        return html_res


class Agent:
    def __init__(self):
        self.client = OpenAI(api_key=global_config.api_key, base_url="https://api.deepseek.com")

    def singel_chat(self, prompt: str):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        res = response.choices[0].message.content
        return res

    def generate_html_template(self, prompt: str):
        res = self.singel_chat(prompt)
        html_res = res.replace('```html', '').replace('```', '').strip()
        return html_res


if __name__ == '__main__':
    agent = Agent()
    prompt = global_config.default_prompt.index_page_prompt + "\n" \
        + "请只返回HTML模板代码，使用Jinja2语法，不要包含其他说明文字。代码中应包含所有必要的CSS和JavaScript代码。"
    template = agent.generate_html_template(prompt)
    print(template)
