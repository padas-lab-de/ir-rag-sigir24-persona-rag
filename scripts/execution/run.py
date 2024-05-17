from persona_rag.core.generate import create_agent_group, create_workflow
from persona_rag.prompts.prompt import Prompt
from datetime import datetime
from tqdm import tqdm
import traceback
import time
import json
import os
MODEL = os.getenv('MODEL')


def main(dataset, topk):
    filename = f'data/data_{dataset}_sampled.jsonl'
    directory = f'logs/{MODEL}/{dataset}/top{topk}'
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    global_memory = '' 

    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in tqdm(enumerate(file)):
            if i >= 100:  
                break
            
            log_filename = f'logs/{MODEL}/{dataset}/top{topk}/{dataset}_idx_{i}.json'
            if os.path.exists(log_filename):
                print(f"Skipping index {i} as log file already exists.")
                continue  
            
            
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
                
            workflow.save_log(log_filename)
