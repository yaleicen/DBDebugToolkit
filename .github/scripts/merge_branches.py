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
        return result
    except subprocess.CalledProcessError as e:
        if "CONFLICT" in e.stderr:  # 检查是否有冲突
            print(f"Merge conflict detected in feature branch. Skipping and moving to the next one.")
            return  # 直接返回，放弃当前分支的合并
        else:  # 其他错误
            print(f"Command failed: {e.stderr}")
        raise e

def merge_branch(source, target):
    print(f"Merging {source} into {target}...")
    run_command(['git', 'checkout', target])
    run_command(['git', 'merge', source])
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

    # 合并单个分支
    if '*' not in target:
        merge_branch(source, target)
    else:
        # 合并到所有匹配的分支
        run_command(['git', 'checkout', 'develop'], cwd=repo_path)  # 确保在 develop 分支
        run_command(['git', 'pull'], cwd=repo_path)
        branches = run_command(['git', 'branch', '-r'], cwd=repo_path).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            try:
                merge_branch(source, "feature/" + fb)
            except subprocess.CalledProcessError:
                pass  # 遇到错误时跳过，继续下一个分支
if __name__ == "__main__":
    main()
