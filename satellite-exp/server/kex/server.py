import csv
import os
import sys
import subprocess

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
    if len(sys.argv) != 3:
        print("Usage: python experiment_mn.py <nginx_path> <nginx_conf_dir>")
        sys.exit(1)

    nginx_path = sys.argv[1]
    nginx_conf_dir = sys.argv[2]

    subprocess.run([nginx_path, "-c", nginx_conf_dir])
