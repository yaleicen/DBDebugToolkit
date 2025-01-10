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

def readyForMerge(source,target):
    if not source or not target:
        logToBuffer("Source and target branches must be specified.")
        exit(1)

    # Merge single branches
    if '*' not in target:
        logToBuffer(f"Merging {source} into {target}: ")
        merge_branch(source, target)
    else:
        # Merge to all matching branches
        logToBuffer(f"Merging {source} into feature/{fb}: ")
        run_command(['git', 'checkout', 'develop'])
        run_command(['git', 'pull'])
        branches = run_command(['git', 'branch', '-r']).stdout.split()
        feature_branches = [b.split('/')[-1] for b in branches if b.startswith('origin/feature/')]
        for fb in feature_branches:
            logToBuffer(f"Merging {source} into feature/{fb}: ")
            merge_branch(source, "feature/" + fb)

    flushLogBuffer()
    if hasError:
        raise



# python .github/scripts/merge_branches.py master release/$branch_name
# python .github/scripts/merge_branches.py develop master
# python .github/scripts/merge_branches.py --source develop --target feature/*

# Merge release/xxx to master
run_command(['git', 'add', '.'])
run_command(['git', 'commit', '-m', '"Update"'])
readyForMerge(source='relsease/1.0.0', target='master')
readyForMerge(source='master', target='develop')
readyForMerge(source='develop', target='feature/*')

