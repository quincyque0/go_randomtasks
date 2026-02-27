import subprocess
import sys
import os

def main():
    group = os.getenv("GROUP", "431")
    sid = os.getenv("STUDENT_ID", "s01")
    
    print(f"Checking tests for {group}/{sid}...")
    
    for i in range(3, 18):
        week = str(i).zfill(2)
        print(f"Week {week}:", end=" ", flush=True)
        try:
            cmd = [sys.executable, "-m", "pytest", f"weeks/week-{week}/tests"]
            env = {**dict(os.environ), "GROUP": group, "STUDENT_ID": sid}
            result = subprocess.run(cmd, capture_output=True, env=env)
            
            if result.returncode == 0:
                print("PASS")
            elif result.returncode == 1:
                print("FAIL (Assertions failed, OK)")
            else:
                print(f"CRASH (code {result.returncode})")
                # print(result.stderr.decode()) # Uncomment for debug
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
