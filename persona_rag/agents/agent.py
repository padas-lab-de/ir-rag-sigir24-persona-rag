import time
import openai
import re
import os
import asyncio
import types
from typing import Union

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")
DEFAULT_PROMPT = os.getenv("DEFAULT_PROMPT")


class Agent:
    ENABLE_TRIMMING = os.getenv("ENABLE_TRIMMING", "false").lower() in (
        "true",
        "1",
        "t",
    )
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "16385"))

    def __init__(self, template=None, model=None, key_map=None):
        self.message = []
        self.model = model
        self.key_map = key_map
        self.last_response = None
        self.init_api_client()
        # Initialize template_list and TEMPLATE based on the type and content of template
        if isinstance(template, str):
            self.TEMPLATE = template
            self.template_list = [template]  # Ensure template_list is not empty
        elif isinstance(template, list) and len(template) > 0:
            self.TEMPLATE = template[0]
            self.template_list = template
        else:
            self.TEMPLATE = DEFAULT_PROMPT  # Use a default prompt if template is None or not a list/str
            self.template_list = [DEFAULT_PROMPT] if DEFAULT_PROMPT else []

        self.func_dic = {
            "default": self.get_output,
            "padding_template": self.padding_template,
        }

    def init_api_client(self):
        if self.model.startswith("gpt"):
            self.api_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.model == "llama3":
            self.api_client = openai.OpenAI(
                api_key=os.getenv("LLAMA_API_KEY"),
                base_url=os.getenv("LLAMA_API_ENDPOINT"),
            )
        elif self.model == "mixtral":
            self.api_client = openai.OpenAI(
                api_key=os.getenv("MIXTRAL_API_KEY"),
                base_url=os.getenv("MIXTRAL_API_ENDPOINT"),
            )
        else:
            raise ValueError(f"Unsupported model: {self.model}")

    def send_message(self):
        self.trim_context_if_enabled()
        assert (
            len(self.message) != 0 and self.message[-1]["role"] != "assistant"
        ), "ERROR in message format"
        try:
            ans = self.api_client.chat.completions.create(
                model=self.model, messages=self.message, temperature=0.2, n=1
            )
            self.parse_message(ans)
            return ans
        except Exception as e:
            print(e)
            time.sleep(20)
            ans = self.api_client.chat.completions.create(
                model=self.model, messages=self.message, temperature=0.2, n=1
            )
            self.parse_message(ans)
            return ans
            # aviod frequently request

    async def send_message_async(self):
        try:
            ans = await self.api_client.chat.completions.acreate(
                model=self.model, messages=self.message, temperature=0.2, n=1
            )
            self.parse_message(ans)
            return ans
        except Exception as e:
            print(e)
            await asyncio.sleep(20)
            ans = await self.api_client.chat.completions.acreate(
                model=self.model, messages=self.message, temperature=0.2, n=1
            )
            self.parse_message(ans)
            return ans

    def padding_template(self, input):
        input = self.key_mapping(input)

        assert self._check_format(input.keys()), f"input lack of the necessary key"

        msg = self.TEMPLATE.format(**input)
        self.message.append({"role": "user", "content": msg})

    def key_mapping(self, input):
        if self.key_map is not None:
            new_input = {}
            for key, val in input.items():
                if key in self.key_map.keys():
                    new_input[self.key_map[key]] = val
                else:
                    new_input[key] = val
            input = new_input
            return input
        else:
            return input

    def _check_format(self, key_list):
        placeholders = re.findall(r"\{([^}]+)\}", self.TEMPLATE)
        for key in placeholders:
            if key not in key_list:
                return False
        return True

    def get_output(self) -> str:
        assert len(self.message) != 0 and self.message[-1]["role"] == "assistant"
        return self.message[-1]["content"]

    def parse_message(self, completion):
        if hasattr(completion, "choices") and completion.choices:
            content = completion.choices[0].message.content 
            role = "assistant"  

            # Logic to handle the parsed message
            if not (self.message and self.message[-1]["role"] == role):
                record = {"role": role, "content": content.strip()}
                self.message.append(record)
                self.last_response = record
        else:
            print("Warning: Unexpected response format received.")

    def regist_fn(self, func, name):
        setattr(self, name, types.MethodType(func, self))
        self.func_dic[name] = getattr(self, name)

    def trim_context_if_enabled(self):
        if self.ENABLE_TRIMMING:
            self.trim_context()

    def trim_context(self):
        total_tokens = sum(
            len(self.message[i]["content"]) for i in range(len(self.message))
        )
        while total_tokens > self.MAX_TOKENS:
            removed_message = self.message.pop(0)
            total_tokens -= len(removed_message["content"])
