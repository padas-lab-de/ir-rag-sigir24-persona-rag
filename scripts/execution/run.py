from PersonaRAG.persona_rag.core.generate import create_agent_group, create_plan
from PersonaRAG.persona_rag.prompts.prompt import Prompt
from datetime import datetime
from tqdm import tqdm
import traceback
import time
import json
import os

def main(dataset, topk):
    filename = f'data/data_{dataset}_sampled.jsonl'
    directory = f'log/{dataset}/top{topk}'
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in tqdm(enumerate(file)):
            try:
                data = json.loads(line)
                question = data['question']
                answers = data['answers']
                passages = data['passages'][:topk]

                input = {
                    'question': question,
                    'passages': passages,
                    '__answers__': answers,
                }

                print(f"{i}. {question}")
                time.sleep(5)
                plan = create_plan(create_agent_group(Prompt()), init_input=input)
                plan.excute()
                
                plan.save_log(f'log/{dataset}/top{topk}/{dataset}_idx_{i}.json')

            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Error at index {i} - {current_time}: {e}")
                traceback.print_exc()
                break