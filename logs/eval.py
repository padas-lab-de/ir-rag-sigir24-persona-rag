import json
import matplotlib.pyplot as plt
import numpy as np
import os
from argparse import ArgumentParser
MODEL = os.getenv('MODEL')

def plot_metrics_comparison(datasets, topk):
    """
    Plots BLEU-Score, Normalized Average Sentence Length, and Normalized Average Syllable Count Comparison for multiple datasets based on the results.json files.
    
    Parameters:
    - datasets: List of dataset names being evaluated.
    - topk: The 'topk' value used in the evaluation.
    """
    # Ensure the metrics directory exists
    os.makedirs('metrics', exist_ok=True)
    
    models = ['PersonaRAG', 'Chain-of-Thought (CoT)', 'VanillaGPT', 'VanillaRAG']
    model_columns = ['cognitive_output', 'cot_output', 'vanilla_chatgpt_output', 'vanilla_rag_output']
    width = 0.15  # the width of the bars
    x = np.arange(len(models))  # the label locations
    
    # Custom flat colors for each dataset
    flat_colors = [
        '#6b96e7',  # NQ (blue)
        '#f5a830',  # WebQ (orange)
        '#e28781'   # TriviaQ (red)
    ]
    
    # Initialize data structures for plotting
    blue_scores = {dataset: [] for dataset in datasets}
    avg_sentence_length = np.zeros(len(models))
    avg_syllable_count = np.zeros(len(models))
    
    for dataset_idx, dataset in enumerate(datasets):
        file_name = f'logs/{MODEL}/{dataset}/top{topk}/results.json'
        if not os.path.exists(file_name):
            print(f"Data not found for {dataset}. Skipping...")
            continue
        
        with open(file_name, 'r') as file:
            data = json.load(file)
        
        # Extract BLEU scores and normalized averages for the specified models
        for i, column in enumerate(model_columns):
            for entry in data:
                if entry['column'] == column:
                    blue_scores[dataset].append(entry['BLEU'])
                    avg_sentence_length[i] += entry['Norm_Avg_Sentence_Length']
                    avg_syllable_count[i] += entry['Norm_Avg_Syllables']
                    break
    
    # Average the sentence length and syllable count across datasets
    avg_sentence_length /= len(datasets)
    avg_syllable_count /= len(datasets)
    
    # Recreate the bar plot as a base layer
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Bar plot for BLEU scores
    for i, (dataset, scores) in enumerate(blue_scores.items()):
        ax1.bar(x + i * width, scores, width, label=dataset, color=flat_colors[i % len(flat_colors)], edgecolor='black', linewidth=1)
    
    # Set labels and title for the bar plot
    ax1.set_ylabel('BLEU-Score')
    ax1.set_title(f'Text Similarity between Chain-of-Note (CoN) and other Methods using Top-{topk} Passages', fontsize=14)
    ax1.set_xticks(x + width * (len(datasets) - 1) / 2)
    ax1.set_xticklabels(models, rotation=45, ha='right', fontsize=12)
    ax1.legend(title='Dataset', loc='center right')
    ax1.grid(False)
    
    # Create a secondary axis for line plots
    ax2 = ax1.twinx()
    ax2.plot(x + width * (len(datasets) - 1) / 2, avg_sentence_length, label='Normalized Avg Sentence Length', marker='o', color='purple')
    ax2.plot(x + width * (len(datasets) - 1) / 2, avg_syllable_count, label='Normalized Avg Syllable Count', marker='s', color='brown')
    
    # Set labels and legends for the secondary axis
    ax2.set_ylabel('Normalized Average Values')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'metrics/comparison_top{topk}.png')
    plt.show()
    
    
def main():
    parser = ArgumentParser()
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--topk', type=int, required=True)
    args = parser.parse_args()

    dataset = args.dataset
    datasets = ['triviaqa', 'webq', 'nq']
    topk = args.topk
    
    
    # Initialize counters for each output type
    num_cognitive_output = 0
    num_cot_output = 0
    num_vanilla_chatgpt_output = 0
    num_guideline_output = 0
    num_vanilla_rag_output = 0
    num_con_output = 0
    num_self_rerank_output = 0

    # Loop through each file in the dataset
    for i in range(500):
        file_path = f'logs/{MODEL}/{dataset}/top{topk}/{i}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            if data['cognitive_output']['cognitive_output_correctness'] == 'True':
                num_cognitive_output += 1
            if data['cot_output']['cot_output_correctness'] == 'True':
                num_cot_output += 1
            if data['vanilla_chatgpt_output']['vanilla_chatgpt_output_correctness'] == 'True':
                num_vanilla_chatgpt_output += 1
            if data['guideline_output']['guideline_output_correctness'] == 'True':
                num_guideline_output += 1
            if data['vanilla_rag_output']['vanilla_rag_output_correctness'] == 'True':
                num_vanilla_rag_output += 1
            if data['con_output']['con_output_correctness'] == 'True':
                num_con_output += 1
            if data['self_rerank_output']['self_rerank_output_correctness'] == 'True':
                num_self_rerank_output += 1

    # Calculate and print the accuracy for each output type
    print(f"cognitive output: {num_cognitive_output/500:.2f}")
    print(f"cot output: {num_cot_output/500:.2f}")
    print(f"vanilla chatgpt output: {num_vanilla_chatgpt_output/500:.2f}")
    print(f"guideline output: {num_guideline_output/500:.2f}")
    print(f"vanilla rag output: {num_vanilla_rag_output/500:.2f}")
    print(f"con output: {num_con_output/500:.2f}")
    print(f"self rerank output: {num_self_rerank_output/500:.2f}")
    
    plot_metrics_comparison(datasets, topk)

if __name__ == "__main__":
    main()