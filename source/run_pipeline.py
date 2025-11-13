import subprocess, sys 

steps = [ 
["python","source/api_get_raw.py"], 
["python","source/mb_classify_hybrid.py"]
] 

for cmd in steps: 
    print("\n"," ".join(cmd)); subprocess.run(cmd, check=True) 
    print("\n Pipeline complete → see /data")