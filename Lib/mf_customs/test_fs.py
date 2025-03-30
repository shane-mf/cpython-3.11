if __name__ == "__main__":
    print("---------original file content:---------")
    with open('/tmp/test.txt', 'r', encoding='utf-8') as file:
        file.seek(0)
        content = file.read()
        print(content)

    # Write a random number to the file
    print("---------write some number...---------")
    for i in range(3):
        with open('/tmp/test.txt', 'a', encoding='utf-8') as file:
            file.write('\n' + str(i))
    
    # Read it back
    print("---------after write, read file content:---------")
    with open('/tmp/test.txt', 'r', encoding='utf-8') as file:
        file.seek(0)
        content = file.read()
        print(content)
