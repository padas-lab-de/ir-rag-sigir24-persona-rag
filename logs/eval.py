import json
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--topk', type=int, required=True)
    args = parser.parse_args()

    dataset = args.dataset
    topk = args.topk

    num_user_profile = 0
    num_contextual_retrieval = 0
    num_live_session = 0
    num_document_ranking = 0
    num_feedback = 0  

    for i in range(500):
        file_path = f'logs/{dataset}/top{topk}/{i}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            if data['user_profile']['user_profile_correctness'] == 'True':
                num_user_profile += 1
            if data['contextual_retrieval']['contextual_retrieval_correctness'] == 'True':
                num_contextual_retrieval += 1
            if data['live_session']['live_session_correctness'] == 'True':
                num_live_session += 1
            if data['document_ranking']['document_ranking_correctness'] == 'True':
                num_document_ranking += 1
            if data['feedback']['feedback_correctness'] == 'True':  
                num_feedback += 1

    print(f"user profile: {num_user_profile/500:.2f}")
    print(f"contextual retrieval: {num_contextual_retrieval/500:.2f}")
    print(f"live session: {num_live_session/500:.2f}")
    print(f"document ranking: {num_document_ranking/500:.2f}")
    print(f"feedback: {num_feedback/500:.2f}") 

if __name__ == "__main__":
    main()