import os
import glob

file_path = './'
if os.path.exists(file_path):
    files = glob.glob(os.path.join(file_path, '*'))
    for f in files:
        print(f)
        # os.remove(f)