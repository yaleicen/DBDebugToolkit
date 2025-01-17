import subprocess
import sys

def run_command(command, cwd=None):
    global hasError
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
        if 'push' in command_str:
            print("----Merging successful!----")
        if 'abort' in command_str:
            print("❌====Fail to merge====❌")
        return result
    except subprocess.CalledProcessError as e:
        if "CONFLICT" in e.stdout:
            print(f"    ❌Error in {command_str}: {e.stdout}")
        else:
            print(f"    ❌Error in {command_str}: {e.stdout}")
        hasError = True
        raise
    except Exception as other:
        print(f"    ❌Error in {command_str}: {other}")
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

def readyForMerge(source,target):
    if not source or not target:
        print("Source and target branches must be specified.")
        exit(1)

    # Merge single branches
    if '*' not in target:
        print(f"Merging {source} into {target}: ")
        merge_branch(source, target)
    else:
        # Merge to all matching branches
        print(f"Merging {source} into {target}: ")
        run_command(['git', 'checkout', 'develop'])
        run_command(['git', 'pull'])
        branches = run_command(['git', 'branch', '-r']).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            print(f"Merging {source} into feature/{fb}: ")
            merge_branch(source, "feature/" + fb)

# Merge release/xxx to master
def startToMerge():
    print("===========================")
    run_command(['git', 'add', '.'])
    run_command(['git', 'commit', '-m', '"Update"'])
    run_command(['git', 'push'])
    readyForMerge(source='release/1.0.2', target='master')
    readyForMerge(source='master', target='develop')
    readyForMerge(source='develop', target='feature/*')
    if hasError:
        raise

startToMerge()
