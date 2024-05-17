import copy
from itertools import islice
from ..prompts.prompt import Prompt
from ..agents.agent import *
from ..agents.group import *
from ..workflows.workflow import *
import json
import os
from datetime import datetime
import traceback

MODEL = os.getenv('MODEL')

def create_agent_group(prompt: Prompt):
    empty_dict = {}
    group = AgentGroup(empty_dict)

    key_map = {
        "user_profile": "user_profile_reply",
        "contextual_retrieval": "contextual_retrieval_reply",
        "live_session": "live_session_reply",
        "document_ranking": "document_ranking_reply",
        "feedback": "feedback_reply",
        "cognitive": "cognitive_reply",
        "vanilla_chatgpt": "vanilla_chatgpt_reply",
        "guideline": "guideline_reply",
        "vanilla_rag": "vanilla_rag_reply",
        "con": "con_reply",
        "self_rerank" : "self_rerank_reply"
    }

    for key, val in prompt.template.items():
        group.add_agent(Agent(template=val, model=MODEL, key_map=key_map), key)
        
    return group


def create_workflow(group: AgentGroup, init_input: dict) -> Workflow:
    """
    init_input: A dict, whose key should match the variable in the template
    the init_input dict should include keys: question, choices_combined, passages
    """
    
    question = init_input.get('question', '')
    passages = init_input.get('passages', [])
    workflow = Workflow(group, current_question=question, current_passages=passages)

    task1_output = workflow.push_workflow(
        create_task(
            agent=workflow.agents.agent_dic["cot"],
            pre_func="padding_template",
            input=init_input,
            post_func="default",
        )
    )

    def prepare_first_round(self: Agent, input):
        if len(self.template_list) > 1:
            self.TEMPLATE = self.template_list[1]
        else:
            self.TEMPLATE = self.template_list[0] if self.template_list else ""
        input[self.name] = self.get_output()
        self.padding_template(input)

    workflow.agents.agent_dic["user_profile"].regist_fn(
        prepare_first_round, "prepare_first_round"
    )
    workflow.agents.agent_dic["contextual_retrieval"].regist_fn(
        prepare_first_round, "prepare_first_round"
    )
    workflow.agents.agent_dic["live_session"].regist_fn(
        prepare_first_round, "prepare_first_round"
    )
    workflow.agents.agent_dic["document_ranking"].regist_fn(
        prepare_first_round, "prepare_first_round"
    )
    workflow.agents.agent_dic["feedback"].regist_fn(
        prepare_first_round, "prepare_first_round"
    )

    new_init_input = copy.deepcopy(init_input)
    new_init_input["reply"] = task1_output

    workflow.push_parallel_workflow(
        [
            create_task(
                agent=workflow.agents.agent_dic["user_profile"],
                pre_func="padding_template",
                input=new_init_input,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["contextual_retrieval"],
                pre_func="padding_template",
                input=new_init_input,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["live_session"],
                pre_func="padding_template",
                input=new_init_input,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["document_ranking"],
                pre_func="padding_template",
                input=new_init_input,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["feedback"],
                pre_func="padding_template",
                input=new_init_input,
                post_func="default",
            ),
        ]
    )

    return workflow
