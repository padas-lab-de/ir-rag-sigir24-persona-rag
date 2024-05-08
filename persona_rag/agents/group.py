from aiohttp import ClientSession
from .agent import Agent
import asyncio
import openai


class AgentGroup:
    def __init__(self,agent_dic={}) -> None:
        self.agent_dic:dict[str,Agent] = agent_dic

    def parallel_send(self,agent_list):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._parallel_send_async(agent_list))

    async def _parallel_send_async(self,agent_list):
        openai.aiosession.set(ClientSession(trust_env=True))
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(agent.send_message_async()) for agent in agent_list]
        await asyncio.gather(*tasks)
        await openai.aiosession.get().close()
    
    def save_all_messages(self,file_address):
        log = {name : agent.message for name,agent in self.agent_dic.items()}
        return log


    def serial_send(self,agent:Agent):
        agent.send_message()


    def add_agent(self,agent: Agent, name: str):
        setattr(self,name,agent)
        if name not in self.agent_dic:
            self.agent_dic[name] = agent
            agent.name = name
        else:
            raise Exception("This name already exists in agent dict")
    
    def del_agent(self, name):
        if name in self.agent_dic:
            del self.agent_dic[name]
            if getattr(self,name,None) != None:
                delattr(self,name)
        else:
            #TODO
            pass
    
    def change_agent(self, agent, name):
        if name in self.agent_dic:
            self.del_agent(name)
            self.add_agent(agent, name)
        else:
            self.add_agent(agent, name)

    
    
        
