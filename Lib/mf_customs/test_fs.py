def read_test_file():
    try:
        with open('/tmp/test.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print("Error: File /tmp/test.txt not found.")
    except UnicodeDecodeError:
        print("Error: Unable to decode file as UTF-8.")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    read_test_file()
