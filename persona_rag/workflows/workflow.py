from ..agents.group import AgentGroup
from ..agents.agent import Agent
from typing import List
import json

class Task:

    def __init__(self, agent, pre_func_name=None, input=None, post_func_name=None, output=None) -> None:
        self.agent = agent
        self.pre_func_name = pre_func_name
        self.input = input 
        self.post_func_name = post_func_name
        self.output = self.agent if output == None else output
        self.relyon = None

    def get_output(self):
        return self.output
    
    def excute_pre_func(self):
        #prepare input
        if isinstance(self.input, Agent):
            self.relyon = self.input
            input = {self.relyon.name:self.input.get_output()}
            self.input = input
        elif isinstance(self.input, list):
            outputs = {}
            self.relyon = []
            for item in self.input:
                if isinstance(item, Agent):
                    self.relyon.append(item)
                    outputs[item.name] = item.get_output()
                else:
                    raise TypeError('if input is a list type, the variable in list should be consistent of type: Agent type')
            self.input = outputs
        elif isinstance(self.input, dict):
            for key, val in self.input.items():
                if isinstance(val,Agent):
                    self.input[key] = val.get_output()

        ret = self.agent.func_dic[self.pre_func_name](self.input)
        return ret
    
    def excute_post_func(self):
        ret = self.agent.func_dic[self.post_func_name]()
        self.output = ret
        return ret

def create_task(agent, pre_func, input, post_func):
    task = Task(agent, pre_func, input, post_func)
    return task


class Workflow:
    def __init__(self, agents: AgentGroup, workflow_list=[]) -> None:
        self.agents = agents
        self.workflow_list = workflow_list

    def init_workflow(self):
        self.workflow_list = []

    def push_workflow(self, task: Task):
        self.workflow_list.append(task)
        return task.output

    def push_parallel_workflow(self, task_list: List[Task]):
        self.workflow_list.append(task_list)
        output_list = [out.output for out in task_list]
        return output_list

    def pop_workflow(self):
        # TODO
        pass

    def get_previous_workflow(self):
        # TODO
        pass

    def execute(self):
        for item in self.workflow_list:
            if isinstance(item, Task):
                item.execute_pre_func()
                self.agents.serial_send(item.agent)
                item.execute_post_func()
            elif isinstance(item, list):
                parallel_agents = []
                for task in item:
                    parallel_agents.append(task.agent)
                    task.execute_pre_func()
                self.agents.parallel_send(parallel_agents)
                for task in item:
                    task.execute_post_func()

    def save_log(self, file_path):
        log = self.agents.save_all_messages(file_path)
        log['question_info'] = self.workflow_list[0].input
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(log, file)




