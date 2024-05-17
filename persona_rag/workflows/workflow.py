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
        self.executed = False

    def get_output(self):
        return self.output
    
    def execute_pre_func(self):
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
    
    def execute_post_func(self):
        ret = self.agent.func_dic[self.post_func_name]()
        self.output = ret
        return ret

def create_task(agent, pre_func, input, post_func):
    task = Task(agent, pre_func, input, post_func)
    return task


class Workflow:
    def __init__(self, agents: AgentGroup, workflow_list=[], global_memory="", current_question="", current_passages=[]) -> None:
        self.agents = agents
        self.current_question = current_question
        self.current_passages = current_passages
        self.workflow_list = workflow_list
        self.global_memory = global_memory

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
        pass

    def get_previous_workflow(self):
        pass

    def execute(self):
        for item in self.workflow_list:
            if isinstance(item, Task):
                self.execute_task(item)
            elif isinstance(item, list):
                for task in item:
                    self.execute_task(task)
                    
        self.execute_cognitive_task()
        self.execute_vanilla_chatgpt_task()
        self.execute_guideline_task()
        self.execute_vanilla_rag_task()
        self.execute_con_task()
        self.execute_self_rerank_task()

    def execute_task(self, task):
        task.execute_pre_func()
        self.agents.serial_send(task.agent) 
        task.execute_post_func()
        
        if task.agent.name in ["user_profile", "contextual_retrieval", "live_session", "document_ranking", "feedback"]:
            self.update_global_memory(task.agent.name, task.get_output())

        
        self.pass_updated_global_memory_to_next_tasks(task)
        
    def execute_cognitive_task(self):
        cot_answer = self.agents.agent_dic["cot"].get_output() 
        cognitive_input = {
            "question": self.current_question,
            "cot_answer": cot_answer,
            "global_memory": self.global_memory
        }
        cognitive_task = create_task(
            agent=self.agents.agent_dic["cognitive"],
            pre_func="padding_template",
            input=cognitive_input,
            post_func="default"
        )
        self.execute_task(cognitive_task)
        
    def execute_vanilla_chatgpt_task(self):
        vanilla_chatgpt_input = {
            "question": self.current_question,
        }
        vanilla_chatgpt_task = create_task(
            agent=self.agents.agent_dic["vanilla_chatgpt"],
            pre_func="padding_template",
            input=vanilla_chatgpt_input,
            post_func="default"
        )
        self.execute_task(vanilla_chatgpt_task)
        
    def execute_guideline_task(self):
        guideline_input = {
            "question": self.current_question,
        }
        guideline_task = create_task(
            agent=self.agents.agent_dic["guideline"],
            pre_func="padding_template",
            input=guideline_input,
            post_func="default"
        )
        self.execute_task(guideline_task)
        
    def execute_self_rerank_task(self):
        self_rerank_input = {
            "question": self.current_question,
            "passages": self.current_passages,
        }
        self_rerank_task = create_task(
            agent=self.agents.agent_dic["self_rerank"],
            pre_func="padding_template",
            input=self_rerank_input,
            post_func="default"
        )
        self.execute_task(self_rerank_task)
        
    def execute_con_task(self):
        con_input = {
            "question": self.current_question,
            "passages": self.current_passages, 
        }
        con_task = create_task(
            agent=self.agents.agent_dic["con"],
            pre_func="padding_template",
            input=con_input,
            post_func="default"
        )
        self.execute_task(con_task)
        
    def execute_vanilla_rag_task(self):
        vanilla_rag_input = {
            "question": self.current_question,
            "passages": self.current_passages, 
        }
        vanilla_rag_task = create_task(
            agent=self.agents.agent_dic["vanilla_rag"],
            pre_func="padding_template",
            input=vanilla_rag_input,
            post_func="default"
        )
        self.execute_task(vanilla_rag_task)
    
    def pass_updated_global_memory_to_next_tasks(self, current_task):
        # Mark the current task as executed
        current_task.executed = True

        # Update global memory for all subsequent unexecuted tasks
        for task in self.workflow_list:
            if isinstance(task, Task) and not task.executed:
                task.input['global_memory'] = self.global_memory
            elif isinstance(task, list):  # For parallel tasks
                for sub_task in task:
                    if not sub_task.executed:
                        sub_task.input['global_memory'] = self.global_memory
        
    def execute_global_memory_update(self, agent_responses):
        """
        Execute the global_memory_update prompt with the latest agent response,
        and update the global memory to only include the 'content' part of the response.
        """
        
        input_for_global_memory_update = {
            "question": self.current_question,
            "agent_responses": json.dumps(agent_responses, ensure_ascii=False),
            "global_memory": self.global_memory
        }

        agent = self.agents.agent_dic["global_memory_update"]
        agent.padding_template(input_for_global_memory_update)
        response = agent.send_message()  
        
        # Check if the response has the expected structure
        if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
            content = response.choices[0].message.content
            self.global_memory = content  
        else:
            print("Warning: Unexpected response format received from global_memory_update agent.")

    def update_global_memory(self, agent_name, agent_response):
        """
        Update the global memory based on the latest agent response.
        """
        # Check if the agent is one of the specified agents before updating
        if agent_name in ["user_profile", "contextual_retrieval", "live_session", "document_ranking", "feedback"]:
            agent_responses = {agent_name: agent_response}
            self.execute_global_memory_update(agent_responses)

    def get_global_memory(self):
        """
        Return the current state of the global memory.
        """
        return self.global_memory

    def save_log(self, file_path):
        log = self.agents.save_all_messages(file_path)
        log['question_info'] = self.workflow_list[0].input
        log['global_memory_update'] = self.global_memory
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(log, file)




