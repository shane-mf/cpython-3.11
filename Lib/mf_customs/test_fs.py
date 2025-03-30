def read_test_file():
    with open('/tmp/test.txt', 'r', encoding='utf-8') as file:
        file.seek(0)
        content = file.read()
        print(content)


def write_number(number: int):
    with open('/tmp/test.txt', 'a', encoding='utf-8') as file:
        file.write('\n' + str(number))

if __name__ == "__main__":
    print("original file content:")
    read_test_file()
    print("----------------------------------")

    # Write a random number to the file
    for i in range(3):
        print(f"write number: {i}")
        write_number(i)
    
    # Read it back
    print("----------------------------------\nafter write, read file content:")
    read_test_file()
