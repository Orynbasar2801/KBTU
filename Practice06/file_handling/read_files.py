# Reading files

with open("example.txt", "r") as file:
    print(file.read())

# Read line by line
with open("example.txt", "r") as file:
    for line in file:
        print(line.strip())