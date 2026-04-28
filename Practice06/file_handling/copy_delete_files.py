import shutil
import os

# Copy file
shutil.copy("../example.txt", "copy_example.txt")

# Delete file safely
if os.path.exists("../copy_example.txt"):
    os.remove("../copy_example.txt")
    print("File deleted")
else:
    print("File not found")