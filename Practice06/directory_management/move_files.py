import shutil
import os

# Ensure directory exists
os.makedirs("test_dir", exist_ok=True)

# Move file
if os.path.exists("../example.txt"):
    shutil.move("../example.txt", "test_dir/example.txt")

# List files in folder
print(os.listdir("test_dir"))