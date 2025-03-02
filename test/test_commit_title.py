import json
import subprocess
import os
import tempfile
import argparse
import random

json_file = 'test/commit_titles.json'

commit_msg_hook = '.git/hooks/commit-msg'

def run_commit_msg_hook(commit_msg, debug=False):    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(commit_msg.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        result = subprocess.run([commit_msg_hook, temp_file_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if debug:
            print(f"Running commit-msg hook for commit title: {commit_msg}")
            print(f"stdout: {result.stdout.decode()}")
            print(f"stderr: {result.stderr.decode()}")

        # returncode 0: pass, 1: fail
        return result.returncode == 0
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def test_commit_titles(debug=False, num_repeats=1):
    with open(json_file, 'r') as f:
        data = json.load(f)

    for repeat in range(num_repeats):
        print(f"\n==================== Running Test Round {repeat + 1} ====================")
        
        random.shuffle(data)

        results = []
        failed_data = []

        for item in data:
            title = item["title"]
            expected_result = item["expected_result"]
            
            success = run_commit_msg_hook(title, debug)
            
            result = "PASS" if success else "FAIL"
            
            final_result = "PASS" if expected_result == result else "FAIL"
            
            if final_result == "FAIL":
                failed_data.append({
                    "title": title,
                    "expected_result": expected_result,
                    "result": result,
                    "final_result": final_result
                })
            
            results.append({
                "title": title,
                "expected_result": expected_result,
                "result": result,
                "final_result": final_result
            })
            
            if debug:
                print("--------------------------------------------------")
                print(f"Commit Title : {title}")
                print(f"Expected Result: {expected_result}")
                print(f"Actual Result  : {result}")
                print(f"Final Result   : {final_result}")
                print("--------------------------------------------------\n\n")


        if failed_data:
            print("\n==================== Test Failures ====================")
            for fail in failed_data:
                print(f"\n[FAIL] Commit Title: {fail['title']}")
                print(f"  Expected Result: {fail['expected_result']}")
                print(f"  Actual Result  : {fail['result']}")
                print(f"  Final Result   : {fail['final_result']}")
                print("=======================================================")
        else:
            print("\nAll test cases passed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test commit-msg hook with commit titles.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode (prints stdout and stderr)')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='Number of iterations for running tests (default is 1)')

    args = parser.parse_args()
    
    if not os.path.exists('.git'):
        print("Error: This script must be run from a Git repository.")
    else:
        test_commit_titles(debug=args.debug, num_repeats=args.iterations)
