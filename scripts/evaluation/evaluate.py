import csv
import numpy as np

correctness_columns = [
    'user_profile_correctness',
    'contextual_retrieval_correctness',
    'live_session_correctness',
    'document_ranking_correctness',
    'feedback_correctness'
]

def calculate_accuracy(data, column):
    correctness_values = [row[column] for row in data]
    accuracy = 100 * np.mean([1 if correctness == 'True' else 0 for correctness in correctness_values])
    return accuracy

def evaluate(dataset, topk):
    file_name = f'log/{dataset}/top{topk}/result.csv'
    with open(file_name, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    for column in correctness_columns:
        column_accuracy = calculate_accuracy(data, column)
        print(f"{file_name} {column} Accuracy: {column_accuracy:.2f}%")
