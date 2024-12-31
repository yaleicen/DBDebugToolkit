import argparse
import os
from github import Github, GithubException

def parse_arguments():
    parser = argparse.ArgumentParser(description='Merge branches in GitHub repository.')
    parser.add_argument('target', help='Target branch to merge into.')
    parser.add_argument('source', nargs='?', help='Source branch to merge from.')
    parser.add_argument('--source', dest='source_arg', help='Alternative source branch.')
    parser.add_argument('--target', dest='target_arg', help='Alternative target branch pattern.')
    return parser.parse_args()

def get_github_instance():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise Exception("GITHUB_TOKEN environment variable is not set.")
    return Github(token)

def merge_branch(github, repo, source, target):
    try:
        base = repo.get_branch(target)
        head = repo.get_branch(source)
        print(f"Merging {source} into {target}...")
        merge_info = repo.merge(base.ref, head.ref)
        print(f"Successfully merged {source} into {target}.")
    except GithubException as e:
        print(f"Failed to merge {source} into {target}: {e}")
        raise e

def main():
    args = parse_arguments()

    source = args.source_arg if args.source_arg else args.source
    target = args.target_arg if args.target_arg else args.target

    if not source or not target:
        print("Source and target branches must be specified.")
        exit(1)

    g = get_github_instance()
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

    if '*' in target:
        # Merge to multiple feature branches
        branches = repo.get_branches()
        feature_branches = [branch.name for branch in branches if branch.name.startswith('feature/')]

        for fb in feature_branches:
            try:
                merge_branch(g, repo, source, fb)
            except GithubException:
                print(f"Skipping {fb} due to merge conflict or error.")
    else:
        # Merge single branch
        merge_branch(g, repo, source, target)

if __name__ == "__main__":
    main()
