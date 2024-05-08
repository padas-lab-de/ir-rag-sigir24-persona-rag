import time
import openai
import re
import asyncio
import types
from typing import Union

openai.api_key = 'sk-<your-api-key>'

MODEL = 'gpt-4'
DEFAULT_PROMPT = ""

class Agent:
    def __init__(self,template, model=MODEL, key_map:Union[dict,None]=None) -> None:
        self.message = []
        if isinstance(template,str):
            self.TEMPLATE = template
        elif isinstance(template,list) and len(template)>1:
            self.TEMPLATE = template[0]
            self.template_list = template
        self.key_map = key_map
        self.model = model
        self.func_dic = {

        }
        self.func_dic['default'] = self.get_output
        self.func_dic['padding_template'] = self.padding_template

    def send_message(self):
        assert len(self.message) != 0 and self.message[-1]['role'] != 'assistant', 'ERROR in message format'
        try:
            ans = openai.ChatCompletion.create(
                model = self.model,
                messages = self.message,
                temperature=0.2,
                n = 1
            )
            self.parse_message(ans)
            return ans
        except Exception as e:
            #TODO
            print(e)
            time.sleep(20)
            ans = openai.ChatCompletion.create(
                model = self.model,
                messages = self.message,
                temperature=0.2,
                n = 1
            )
            self.parse_message(ans)
            return ans
            #aviod frequently request

    async def send_message_async(self):
        #TODO add try-expect block
        try:
            ans = await openai.ChatCompletion.acreate(
                model = self.model,
                messages = self.message,
                temperature=0.2,
                n=1
            )
            self.parse_message(ans)
            return ans
        except Exception as e:
            print(e)
            await asyncio.sleep(20)
            ans = await openai.ChatCompletion.acreate(
                model = self.model,
                messages = self.message,
                temperature=0.2,
                n=1
            )
            self.parse_message(ans)
            return ans

    def padding_template(self, input):
        input = self.key_mapping(input)

        assert self._check_format(input.keys()), f"input lack of the necessary key"

        msg = self.TEMPLATE.format(**input)
        self.message.append({
            'role':'user',
            'content':msg
        })

    def key_mapping(self,input):
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

    def _check_format(self,key_list):
        placeholders = re.findall(r'\{([^}]+)\}', self.TEMPLATE)
        for key in placeholders:
            if key not in key_list:
                return False
        return True


    def get_output(self)->str:
        assert len(self.message) != 0 and self.message[-1]['role'] == 'assistant'
        return self.message[-1]['content']
    
    def parse_message(self, completion):
        content =  completion['choices'][0]['message']['content']
        role = completion['choices'][0]['message']['role']
        record =  {'role':role, 'content':content}
        self.message.append(record)
        return record
    
    def regist_fn(self, func, name):
        setattr(self,name,types.MethodType(func,self))
        self.func_dic[name] = getattr(self,name)


