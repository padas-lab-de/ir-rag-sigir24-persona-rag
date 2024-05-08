import copy
from itertools import islice
from ..prompts.prompt import Prompt
from ..agents.agent import *
from ..agents.group import *
from ..workflows.workflow import *
import json
from datetime import datetime
import traceback


def create_agent_group(prompt: Prompt):
    empty_dict = {}
    group = AgentGroup(empty_dict)

    key_map = {
        "user_profile": "user_profile_reply",
        "contextual_retrieval": "contextual_retrieval_reply",
        "live_session": "live_session_reply",
        "document_ranking": "document_ranking_reply",
        "feedback": "feedback_reply",
    }

    for key, val in prompt.template.items():
        group.add_agent(Agent(template=val, model="gpt-4", key_map=key_map), key)
    return group


def create_workflow(group: AgentGroup, init_input: dict) -> Workflow:
    """
    init_input: A dict, whose key should match the variable in the template
    the init_input dict should include keys: question, choices_combined, passages
    """

    workflow = Workflow(group)

    task1_output = workflow.push_workflow(
        create_task(
            agent=workflow.agents.agent_dic["cot"],
            pre_func="padding_template",
            input=init_input,
            post_func="default",
        )
    )

    def prepare_first_round(self: Agent, input):
        self.TEMPLATE = self.template_list[1]
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

    first_round_input = copy.deepcopy(init_input)
    first_round_input["reply"] = task1_output
    origin_cot = first_round_input

    workflow.push_parallel_workflow(
        [
            create_task(
                agent=workflow.agents.agent_dic["anchoring"],
                pre_func="prepare_first_round",
                input=origin_cot,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["associate"],
                pre_func="prepare_first_round",
                input=origin_cot,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["logician"],
                pre_func="prepare_first_round",
                input=origin_cot,
                post_func="default",
            ),
            create_task(
                agent=workflow.agents.agent_dic["cognition"],
                pre_func="prepare_first_round",
                input=origin_cot,
                post_func="default",
            ),
        ]
    )

    return workflow
