import subprocess
import sys

def main():
    for i in range(3, 18):
        week = str(i).zfill(2)
        print(f"Testing Week {week}...", end=" ", flush=True)
        try:
            cmd = [sys.executable, "-m", "pytest", f"weeks/week-{week}/tests"]
            result = subprocess.run(cmd, capture_output=True, env={**dict(os.environ), "GROUP": "ИКС-431", "STUDENT_ID": "s01"})
            
            if result.returncode == 0:
                print("PASS")
            elif result.returncode == 1:
                print("FAIL (as expected)")
            else:
                print(f"CRASH (code {result.returncode})")
                print(result.stderr.decode())
        except Exception as e:
            print(f"ERROR: {e}")

import os
if __name__ == "__main__":
    main()
