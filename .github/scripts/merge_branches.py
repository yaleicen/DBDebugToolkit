import argparse
import os
import subprocess

def run_command(command, cwd=None):
    command_str = ' '.join(command)
    print(f"Executing command: {command_str}")  # 打印完整的命令
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"result.stdout == {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")
        raise e

def merge_branch(source, target):
    print(f"Merging {source} into {target}...")
    run_command(['git', 'checkout', target])
    run_command(['git', 'merge', source])
    run_command(['git', 'push', 'origin', target])

def main():
    print("开始：")
    parser = argparse.ArgumentParser(description='Merge branches using Git commands.')
    parser.add_argument('target', nargs='?', help='Target branch to merge into.')
    parser.add_argument('source', nargs='?', help='Source branch to merge from.')
    parser.add_argument('--source', dest='source_arg', help='Alternative source branch.')
    parser.add_argument('--target', dest='target_arg', help='Alternative target branch pattern.')
    args = parser.parse_args()
    print(f"args == ：{args}")

    source = args.source_arg if args.source_arg else args.source
    target = args.target_arg if args.target_arg else args.target
    print(f"source == ：{source}, target == {target}")
    if not source or not target:
        print("Source and target branches must be specified.")
        exit(1)

    # 获取仓库路径
    repo_path = os.getenv('GITHUB_WORKSPACE')
    if not repo_path:
        raise Exception("GITHUB_WORKSPACE environment variable is not set.")

    # 合并单个分支
    if '*' not in target:
        print(f"分支名称1：{target}")
        merge_branch(source, target)
    else:
        print(f"分支名称2：{repo_path}")
        # 合并到所有匹配的分支
        run_command(['git', 'checkout', 'develop'], cwd=repo_path)  # 确保在 develop 分支
        run_command(['git', 'pull'], cwd=repo_path)
        branches = run_command(['git', 'branch', '-r'], cwd=repo_path).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        print(f"分支名称3：{feature_branches}")
        for fb in feature_branches:
            print(f"分支名称：{fb}")
            merge_branch(source, "/feature/"+fb)

if __name__ == "__main__":
    main()
