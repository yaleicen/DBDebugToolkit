import argparse
import os
import subprocess

error_list = []  # 用于存储错误信息

def run_command(command, cwd=None):
    command_str =' '.join(command)
    print(f"    {command_str}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if "CONFLICT" in e.stdout:
            error_list.append(f"Error 3 in {command_str}: {e.stdout}")  # 记录错误
            return
        else:
            error_list.append(f"Error 2 in {command_str}: {e.stdout}")  # 记录错误
        raise e
    except Exception as other:
        error_list.append(f"Error 1 in {command_str}: {other}")  # 记录错误
        raise other

def merge_branch(source, target):
    run_command(['git', 'checkout', target])
    run_command(['git', 'pull'])
    try:
        run_command(['git','merge', source])
    except :
        run_command(['git','merge', '--abort'], cwd=repo_path)
    else:
        run_command(['git', 'push', 'origin', target])

def main():
    parser = argparse.ArgumentParser(description='Merge branches using Git commands.')
    parser.add_argument('target', nargs='?', help='Target branch to merge into.')
    parser.add_argument('source', nargs='?', help='Source branch to merge from.')
    parser.add_argument('--source', dest='source_arg', help='Alternative source branch.')
    parser.add_argument('--target', dest='target_arg', help='Alternative target branch pattern.')
    args = parser.parse_args()

    source = args.source_arg if args.source_arg else args.source
    target = args.target_arg if args.target_arg else args.target
    if not source or not target:
        print("Source and target branches must be specified.")
        exit(1)

    # 获取仓库路径
    repo_path = os.getenv('GITHUB_WORKSPACE')
    if not repo_path:
        raise Exception("GITHUB_WORKSPACE environment variable is not set.")

    print(f"Merging {source} into {target}: ")
    # 合并单个分支
    if '*' not in target:
        merge_branch(source, target)
    else:
        # 合并到所有匹配的分支
        run_command(['git', 'checkout', 'develop'], cwd=repo_path)
        run_command(['git', 'pull'], cwd=repo_path)
        branches = run_command(['git', 'branch', '-r'], cwd=repo_path).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            merge_branch(source, "feature/" + fb)

    if error_list:
        raise Exception(f"Errors for merging {source} into {target}:\n" + '\n'.join(error_list))

if __name__ == "__main__":
    main()
