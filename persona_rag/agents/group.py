from aiohttp import ClientSession
from .agent import Agent
import asyncio

class AgentGroup:
    def __init__(self, agent_dic={}):
        self.agent_dic: dict[str, Agent] = agent_dic

    def parallel_send(self, agent_list):
        asyncio.run(self._parallel_send_async(agent_list))

    async def _parallel_send_async(self, agent_list):
        async with ClientSession(trust_env=True) as session:
            tasks = [agent.send_message_async() for agent in agent_list]
            await asyncio.gather(*tasks)

    def save_all_messages(self, file_address):
        log = {name: agent.message for name, agent in self.agent_dic.items()}
        return log

    def serial_send(self, agent: Agent):
        agent.send_message()

    def add_agent(self, agent: Agent, name: str):
        if name not in self.agent_dic:
            self.agent_dic[name] = agent
            agent.name = name
            setattr(self, name, agent)
        else:
            raise Exception("This name already exists in agent dict")

    def del_agent(self, name):
        if name in self.agent_dic:
            del self.agent_dic[name]
            if hasattr(self, name):
                delattr(self, name)

    def change_agent(self, agent, name):
        self.del_agent(name)
        self.add_agent(agent, name)