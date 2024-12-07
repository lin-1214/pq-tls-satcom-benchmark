import csv
import os
import sys
from tqdm import tqdm
import subprocess

MEASUREMENTS_PER_TIMER = 100
TIMERS = 10

def run_subprocess(command, working_dir='.', expected_returncode=0):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir
    )
    if(result.stderr):
        print(result.stderr)
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

if __name__ == "__main__":
    subprocess.run(["ls", "-l"])
