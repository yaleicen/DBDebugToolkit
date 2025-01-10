import argparse
import os
import subprocess
import sys

logBuffer = []

def logToBuffer(message):
    """将日志消息添加到缓冲区"""
    logBuffer.append(message)

def flushLogBuffer():
    """将所有缓存的日志消息一次性输出到标准错误"""
    for message in logBuffer:
        print(message, file=sys.stderr)
    # 清空缓冲区
    logBuffer.clear()


hasError = False

def run_command(command, cwd=None):
    command_str =' '.join(command)
    logToBuffer(f"    {command_str}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if 'push' in command_str:
            logToBuffer("Merging successful!")
        return result
    except subprocess.CalledProcessError as e:
        if "CONFLICT" in e.stdout:
            logToBuffer(f"Error in {command_str}: {e.stdout}")  # 记录错误
        else:
            logToBuffer(f"Error in {command_str}: {e.stdout}")  # 记录错误
        hasError = True
        raise
    except Exception as other:
        logToBuffer(f"Error in {command_str}: {other}")  # 记录错误
        hasError = True
        raise

def merge_branch(source, target):
    run_command(['git', 'checkout', target])
    run_command(['git', 'pull'])
    try:
        run_command(['git','merge', source])
    except :
        run_command(['git','merge', '--abort'])
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
        logToBuffer("Source and target branches must be specified.")
        exit(1)

    # 获取仓库路径
    repo_path = os.getenv('GITHUB_WORKSPACE')
    if not repo_path:
        raise Exception("GITHUB_WORKSPACE environment variable is not set.")

    # 合并单个分支
    if '*' not in target:
        logToBuffer(f"Merging {source} into {target}: ")
        merge_branch(source, target)
    else:
        # 合并到所有匹配的分支
        run_command(['git', 'checkout', 'develop'], cwd=repo_path)
        run_command(['git', 'pull'], cwd=repo_path)
        branches = run_command(['git', 'branch', '-r'], cwd=repo_path).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            logToBuffer(f"Merging {source} into feature/{fb}: ")
            merge_branch(source, "feature/" + fb)

    flushLogBuffer()
    if hasError:
        raise Exception("Error: Some branch merges fail")

if __name__ == "__main__":
    main()
