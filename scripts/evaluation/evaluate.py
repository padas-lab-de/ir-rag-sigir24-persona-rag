import csv
import numpy as np
from collections import Counter
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
import textstat
import ast  
from nltk.stem.porter import PorterStemmer
from string import punctuation
import json
import os
MODEL = os.getenv('MODEL')


def calculate_f1(predicted, truths):
    all_scores = []
    for truth in truths:
        scores = []
        pred_tokens = word_tokenize(predicted.lower())
        truth_tokens = word_tokenize(truth.lower())
        common_tokens = Counter(pred_tokens) & Counter(truth_tokens)
        num_same = sum(common_tokens.values())
        if num_same == 0:
            scores.append(0)
        else:
            precision = 1.0 * num_same / len(pred_tokens)
            recall = 1.0 * num_same / len(truth_tokens)
            f1 = (2 * precision * recall) / (precision + recall)
            scores.append(f1)
        all_scores.append(np.mean(scores))
    return np.mean(all_scores)

def calculate_em(predicted, truths):
    scores = [int(predicted.lower().strip() == truth.lower().strip()) for truth in truths]
    return np.mean(scores)

def pre_scan_for_max_values(data, output_columns):
    max_length = 0
    max_syll = 0
    for row in data:
        for column in output_columns:
            predicted = row[column]
            length = calculate_sentence_length(predicted)
            syllables = calculate_syllables(predicted)
            max_length = max(max_length, length)
            max_syll = max(max_syll, syllables)
    return max_length, max_syll

def preprocess_text(text):
    stemmer = PorterStemmer()
    tokens = word_tokenize(text.lower())
    tokens = [stemmer.stem(token) for token in tokens if token not in punctuation]
    return tokens

def calculate_bleu(predicted, truths):
    scores = []
    for truth in truths:
        reference = preprocess_text(truth)
        candidate = preprocess_text(predicted)
        score = sentence_bleu(
            [reference], 
            candidate, 
            weights=(0.5, 0.5, 0, 0),  
            smoothing_function=SmoothingFunction().method1  
        )
        scores.append(score)
    return np.mean(scores)

def calculate_accuracy(correctness_values):
    return 100 * np.mean([1 if val == 'True' else 0 for val in correctness_values])

def calculate_sentence_length(predicted):
    tokens = word_tokenize(predicted)
    return len(tokens)

def calculate_syllables(predicted):
    return textstat.syllable_count(predicted)

def calculate_partial_match(predicted, truths, threshold=0.5):
    predicted_tokens = set(word_tokenize(predicted.lower()))
    scores = []
    for truth in truths:
        truth_tokens = set(word_tokenize(truth.lower()))
        common_tokens = predicted_tokens.intersection(truth_tokens)
        if len(predicted_tokens) == 0 or len(truth_tokens) == 0:
            score = 0
        else:
            score = len(common_tokens) / max(len(predicted_tokens), len(truth_tokens))
        scores.append(score)
    return 1 if np.mean(scores) >= threshold else 0

def evaluate(dataset, topk):
    file_name = f'logs/{MODEL}/{dataset}/top{topk}/result.csv'
    with open(file_name, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    output_columns = [
        'cognitive_output', 'cot_output', 'vanilla_chatgpt_output',
        'guideline_output', 'vanilla_rag_output', 'con_output', 'self_rerank_output'
    ]
    
    max_sentence_length, max_syllables = pre_scan_for_max_values(data, output_columns)
    
    # Initialize a dictionary to hold scores for each output column
    column_scores = {column: {'f1_scores': [], 'em_scores': [], 'pm_scores': [], 'accuracy_scores': [], 'bleu_scores': [], 'norm_sentence_lengths': [], 'norm_syllable_counts': []} for column in output_columns}
    
    for row in data:
        truth = ast.literal_eval(row['true_answer']) if '[' in row['true_answer'] else [row['true_answer']]
        con_output = row['con_output']  
        
        for column in output_columns:
            predicted = row[column]
            
            f1_score = calculate_f1(predicted, truth)
            em_score = calculate_em(predicted, truth)
            pm_score = calculate_partial_match(predicted, truth, threshold=0.2)
            accuracy = calculate_accuracy([row[column.replace('_output', '_correctness')]])
            bleu_score = calculate_bleu(predicted, [con_output])
            norm_sentence_length = calculate_sentence_length(predicted) / max_sentence_length
            norm_syllable_count = calculate_syllables(predicted) / max_syllables
            
            # Append the scores to the respective lists in the dictionary
            column_scores[column]['f1_scores'].append(f1_score)
            column_scores[column]['em_scores'].append(em_score)
            column_scores[column]['pm_scores'].append(pm_score)
            column_scores[column]['accuracy_scores'].append(accuracy)
            column_scores[column]['bleu_scores'].append(bleu_score)
            column_scores[column]['norm_sentence_lengths'].append(norm_sentence_length)
            column_scores[column]['norm_syllable_counts'].append(norm_syllable_count)
    
    # Print the aggregated scores for each output column
    results = []
    
    for column, scores in column_scores.items():
        # print(f"{column}:")
        # print(f"  F1: {np.mean(scores['f1_scores']):.2f}, PM: {np.mean(scores['pm_scores']):.2f}, EM: {np.mean(scores['em_scores']):.2f}, Accuracy: {np.mean(scores['accuracy_scores']):.2f}%, BLEU-2: {np.mean(scores['bleu_scores']):.2f}, Norm Avg Sentence Length: {np.mean(scores['norm_sentence_lengths']):.2f}, Norm Avg Syllables: {np.mean(scores['norm_syllable_counts']):.2f}\n")
        
        result = {
            'column': column,
            'F1': np.mean(scores['f1_scores']),
            'EM': np.mean(scores['em_scores']),
            'PM': np.mean(scores['pm_scores']),
            'Accuracy': np.mean(scores['accuracy_scores']),
            'BLEU': np.mean(scores['bleu_scores']),
            'Norm_Avg_Sentence_Length': np.mean(scores['norm_sentence_lengths']),
            'Norm_Avg_Syllables': np.mean(scores['norm_syllable_counts'])
        }
        
        results.append(result)
    
    # Save results to a JSON file
    results_file_name = f'logs/{MODEL}/{dataset}/top{topk}/results.json'
    with open(results_file_name, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    print(f"Results saved to {results_file_name}")
    