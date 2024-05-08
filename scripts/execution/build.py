import json
import os
import csv

def main(args):
    dataset = args.dataset
    topk = args.topk

    def acc(output):
        correctness = 'True' if any(answer.lower() in output.lower() for answer in answer_key) else 'False'
        return correctness

    csv_file_path = f'log/{dataset}/top{topk}/result.csv'
    csv_columns = ['id', 'user_profile_output', 'user_profile_correctness', 'contextual_retrieval_output', 'contextual_retrieval_correctness',
                   'live_session_output', 'live_session_correctness', 'document_ranking_output', 'document_ranking_correctness', 'feedback_output', 'feedback_correctness', 'true_answer']

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        csv_writer.writeheader()

        for i in range(500):
            file_path = f'log/{dataset}/top{topk}/{dataset}_idx_{i}.json'

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    answer_key = data["question_info"]["__answers__"]

                    user_profile_output = data["user_profile"][-1]["content"]
                    user_profile_correctness = acc(user_profile_output)

                    contextual_retrieval_output = data["contextual_retrieval"][-1]["content"]
                    contextual_retrieval_correctness = acc(contextual_retrieval_output)

                    live_session_output = data["live_session"][-1]["content"]
                    live_session_correctness = acc(live_session_output)

                    document_ranking_output = data["document_ranking"][-1]["content"]
                    document_ranking_correctness = acc(document_ranking_output)

                    feedback_output = data["feedback"][-1]["content"]
                    feedback_correctness = acc(feedback_output)

                    csv_writer.writerow(
                        {'id': i, 'user_profile_output': user_profile_output, 'user_profile_correctness': user_profile_correctness,
                         'contextual_retrieval_output': contextual_retrieval_output, 'contextual_retrieval_correctness': contextual_retrieval_correctness,
                         'live_session_output': live_session_output, 'live_session_correctness': live_session_correctness,
                         'document_ranking_output': document_ranking_output, 'document_ranking_correctness': document_ranking_correctness,
                         'feedback_output': feedback_output, 'feedback_correctness': feedback_correctness,
                         'true_answer': answer_key})
            else:
                print(f"File not found: {file_path}")

    print("CSV file created successfully.")