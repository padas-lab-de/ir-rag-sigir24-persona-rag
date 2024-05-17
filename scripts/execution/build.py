import json
import os
import csv
MODEL = os.getenv('MODEL')


def main(dataset, topk):
    # Load the dataset file and store answers in a dictionary
    dataset_file_path = f'data/data_{dataset}_sampled.jsonl'
    answers_dict = {}
    with open(dataset_file_path, 'r', encoding='utf-8') as dataset_file:
        for idx, line in enumerate(dataset_file):  
            data = json.loads(line)
            answers_dict[idx] = data["answers"] 

    def acc(output, answer_key):
        correctness = 'True' if any(answer.lower() in output.lower() for answer in answer_key) else 'False'
        return correctness

    csv_file_path = f'logs/{MODEL}/{dataset}/top{topk}/result.csv'
    csv_columns = ['id', 
                   'user_profile_output', 'user_profile_correctness', 
                   'contextual_retrieval_output', 'contextual_retrieval_correctness',
                   'live_session_output', 'live_session_correctness', 
                   'document_ranking_output', 'document_ranking_correctness', 
                   'feedback_output', 'feedback_correctness', 
                   'cot_output', 'cot_correctness',  
                   'cognitive_output', 'cognitive_correctness', 
                   'vanilla_chatgpt_output', 'vanilla_chatgpt_correctness',  
                   'guideline_output', 'guideline_correctness', 
                   'vanilla_rag_output', 'vanilla_rag_correctness',  
                   'con_output', 'con_correctness', 
                   'self_rerank_output', 'self_rerank_correctness', 
                   'true_answer']

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        csv_writer.writeheader()

        for i in range(500):
            file_path = f'logs/{MODEL}/{dataset}/top{topk}/{dataset}_idx_{i}.json'

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    answer_key = answers_dict.get(i)
                    row_data = {'id': i, 'true_answer': answer_key}
                    
                    for element in ['user_profile', 'contextual_retrieval', 'live_session', 'document_ranking', 'feedback', 
                                    'cot', 'cognitive', 'vanilla_chatgpt', 'guideline', 'vanilla_rag', 'con', 'self_rerank']:
                        if element in data: 
                            assistant_outputs = [item for item in data[element] if item.get("role") == "assistant"]
                            output = assistant_outputs[-1]["content"]
                            correctness = acc(output, answer_key)
                            row_data[f'{element}_output'] = output
                            row_data[f'{element}_correctness'] = correctness
                        else:
                            row_data[f'{element}_output'] = 'N/A'
                            row_data[f'{element}_correctness'] = 'N/A'

                    csv_writer.writerow(row_data)
            else:
                print(f"File not found: {file_path}")

    print("CSV file created successfully.")