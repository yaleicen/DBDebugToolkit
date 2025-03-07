import argparse
import os
import subprocess
import sys

logBuffer = []

def logToBuffer(message):
    logBuffer.append(message)

def flushLogBuffer():
    for message in logBuffer:
        print(message, file=sys.stderr)
    logBuffer.clear()


hasError = False

def run_command(command, cwd=None):
    global hasError
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
            logToBuffer("----Merging successful!----")
        if 'abort' in command_str:
            logToBuffer("❌====Fail to merge====❌")
        return result
    except subprocess.CalledProcessError as e:
        if "CONFLICT" in e.stdout:
            logToBuffer(f"    ❌Error in {command_str}: {e.stdout}")
        else:
            logToBuffer(f"    ❌Error in {command_str}: {e.stdout}")
        hasError = True
        raise
    except Exception as other:
        logToBuffer(f"    ❌Error in {command_str}: {other}")
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
    args = parser.parse_args()

    source = args.source
    target = args.target
    if not source or not target:
        raise Exception("❌ Source and target branches must be specified. ❌")

    # Gets the code repository path
    repo_path = os.getenv('GITHUB_WORKSPACE')
    if not repo_path:
        raise Exception("❌ GITHUB_WORKSPACE environment variable is not set. ❌")

    # Merge single branches
    if '*' not in target:
        logToBuffer(f"Merging {source} into {target}: ")
        try:
            merge_branch(source, target)
        except:
            flushLogBuffer()
            raise Exception("❌ Encounterd some errors in merging branches ❌")
    else:
        # Merge to all matching branches
        logToBuffer(f"Reday to merge {source} into {target}: ")
        run_command(['git', 'checkout', 'develop'], cwd=repo_path)
        run_command(['git', 'pull'], cwd=repo_path)
        branches = run_command(['git', 'branch', '-r'], cwd=repo_path).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            logToBuffer(f"Merging {source} into feature/{fb}: ")
            try:
                merge_branch(source, "feature/" + fb)
            except Exception as e:
                logToBuffer(f"    ❌Error in merging {source} into feature/{fb}: {e}")
                continue
            
    flushLogBuffer()
    if hasError:
        raise Exception("❌ Encounterd some errors in merging branches ❌")

if __name__ == "__main__":
    main()
