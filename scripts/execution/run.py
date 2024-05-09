from persona_rag.core.generate import create_agent_group, create_workflow
from persona_rag.prompts.prompt import Prompt
from datetime import datetime
from tqdm import tqdm
import traceback
import time
import json
import os


def main(dataset, topk):
    filename = f'data/data_{dataset}_sampled.jsonl'
    directory = f'logs/{dataset}/top{topk}'
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    global_memory = '' 

    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in tqdm(enumerate(file)):
            if i >= 1:  
                break
            try:
                data = json.loads(line)
                question = data['question']
                answers = data['answers']
                passages = data['passages'][:topk]

                input = {
                    'question': question,
                    'passages': passages,
                    'global_memory': global_memory,
                    '__answers__': answers,
                }

                print(f"{i}. {question}")
                time.sleep(5)
                agent_group = create_agent_group(Prompt())
                workflow = create_workflow(agent_group, init_input=input)
                workflow.execute()
                
                global_memory = workflow.get_global_memory()
                
                workflow.save_log(f'logs/{dataset}/top{topk}/{dataset}_idx_{i}.json')

            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Error at index {i} - {current_time}: {e}")
                traceback.print_exc()
                break