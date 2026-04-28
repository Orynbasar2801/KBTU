# *args example
def sum_all(*numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_all(1, 2, 3, 4))

# **kwargs example
def print_info(**data):
    for key, value in data.items():
        print(key, ":", value)

print_info(name="Ali", age=20)