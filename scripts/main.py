import argparse
from execution.run import main as run_main
from execution.build import main as build_main
from evaluation.evaluate import main as evaluate_main

def main():
    parser = argparse.ArgumentParser(description="Control script for running PersonaRAG functionalities")
    subparsers = parser.add_subparsers(title="Commands", description="Available commands", help="Description")

    # Sub-parser for the 'run' command
    parser_run = subparsers.add_parser('run', help='Run the model')
    parser_run.add_argument('--dataset', required=True, help='Dataset name')
    parser_run.add_argument('--topk', type=int, required=True, help='Top K passages to consider')
    parser_run.set_defaults(func=run_main)

    # Sub-parser for the 'build' command
    parser_build = subparsers.add_parser('build', help='Build results into a CSV')
    parser_build.add_argument('--dataset', required=True, help='Dataset name')
    parser_build.add_argument('--topk', type=int, required=True, help='Top K passages to consider')
    parser_build.set_defaults(func=build_main)

    # Sub-parser for the 'evaluate' command
    parser_evaluate = subparsers.add_parser('evaluate', help='Evaluate the model outputs')
    parser_evaluate.add_argument('--dataset', required=True, help='Dataset name')
    parser_evaluate.add_argument('--topk', type=int, required=True, help='Top K passages to consider')
    parser_evaluate.set_defaults(func=lambda args: evaluate_main(args.dataset, args.topk))

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()